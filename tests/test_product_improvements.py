import pytest
import pymupdf
from mediguide.answer_intent import matches_intent, evidence_sentences
from mediguide.claim_tracker import policy_items
from mediguide.documents import chunk_pages
from mediguide.ocr_review import read_review_pages
from mediguide import privacy
from mediguide.vectorstore import VectorStore


@pytest.mark.parametrize("question,unrelated,relevant", [
    ("What is the iron dose?", "Iron deficiency can cause anemia.", "Dose: 8 mg daily."),
    ("What are asthma symptoms?", "Asthma is a condition of the airways.", "Symptoms include wheezing and cough."),
    ("What are drug warnings?", "This medicine comes as tablets.", "Warning: do not use if allergic."),
    ("What causes anemia?", "Anemia is a blood disorder.", "Anemia can result due to blood loss."),
    ("What is the treatment?", "The condition affects the airways.", "Treatment is reviewed by your clinician."),
    ("When is follow-up?", "The patient was seen at the clinic.", "Follow-up in 7 days."),
])
def test_exact_intent(question, unrelated, relevant):
    assert not matches_intent(question, unrelated)
    assert matches_intent(question, relevant)


def test_highlights_only_verbatim_support():
    assert evidence_sentences("Follow-up in 7 days. [S1]", "S1", "Follow-up in 7 days.") == ["Follow-up in 7 days."]
    assert not evidence_sentences("You are healthy. [S1]", "S1", "Follow-up in 7 days.")


def test_claim_scope_and_conditions():
    chunks = chunk_pages([(2, "You must submit the claim form. If requested, provide a medical report.")], "policy.pdf", "insurance")
    chunks += chunk_pages([(1, "You must submit receipts.")], "other.pdf", "insurance")
    rows = policy_items(chunks, "policy.pdf")
    assert len(rows) == 2
    assert rows[1]["kind"].startswith("Optional / conditional")
    assert all(r["page"] == 2 for r in rows)


def test_native_pdf_review_and_bad_upload():
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((50, 50), "Medicine: Demo A | Dose: 1 tablet")
        data = doc.tobytes()
    pages = read_review_pages(data)
    assert "Demo A" in pages[0]["original"]
    assert pages[0]["image"].startswith(b"\x89PNG")
    with pytest.raises(ValueError):
        read_review_pages(b"not a PDF")


def test_user_storage_isolation_and_deletion(tmp_path, monkeypatch):
    monkeypatch.setattr(privacy, "DATA_DIR", tmp_path)
    token = privacy.identity.set(None)
    try:
        privacy.set_identity("https://accounts.google.com", "alice")
        a = privacy.database_path()
        store = VectorStore("patient")
        store.add(chunk_pages([(1, "Synthetic confidential note.")], "note.pdf", "patient"))
        privacy.set_identity("https://accounts.google.com", "bob")
        assert privacy.database_path() != a
        assert not VectorStore("patient").chunks
        privacy.set_identity("https://accounts.google.com", "alice")
        assert len(VectorStore("patient").chunks) == 1
        VectorStore("patient").delete_source("note.pdf")
        assert not VectorStore("patient").chunks
    finally:
        privacy.identity.reset(token)


def test_hindi_question_normalization():
    from mediguide.questions import normalize_question
    assert normalize_question("मधुमेह क्या है") == "diabetes what is"


def test_new_screens_render():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.button(key="nav_ocr").click().run()
    assert not app.exception
    app.button(key="nav_Settings & privacy").click().run()
    assert not app.exception


def test_auth_required_stops_before_private_content(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("MEDIGUIDE_AUTH_REQUIRED", "true")
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    assert not app.exception
    assert any(b.label == "Continue with Google" for b in app.button)
    assert not any(b.key == "nav_schedule" for b in app.button)
