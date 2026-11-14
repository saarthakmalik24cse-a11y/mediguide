import math
import pytest
from mediguide.health_tools import bmi_answer, bmi_chat, bmi_value, cut_answer


def test_uploaded_lab_overview_with_general_question(tmp_path, monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from mediguide import privacy

    monkeypatch.setattr(privacy, "index_path", lambda route: tmp_path / "indexes")
    monkeypatch.setattr(privacy, "database_path", lambda: tmp_path / "history.db")
    filename = "synthetic_lab_report.pdf"
    pdf = Path("data/samples", filename).read_bytes()
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.button(key="nav_Lab report explainer").click().run()
    app.file_uploader(key="upload_lab").upload(filename, pdf, "application/pdf").run()
    app.button(key="index_lab").click().run()
    assert app.selectbox(key="source_lab").value == filename
    app.chat_input(key="chat_lab").set_value("now explain my report what all things i have to improve").run()
    assert not app.exception
    reply = app.session_state["messages"][f"lab:{filename}"][-1]
    assert "1 of 3 readable results" in reply["content"]
    assert "11.2 g/dL" in reply["content"]
    assert len(reply["citations"]) == 3
    assert all(cite["source"] == filename and cite["page"] == 1 for cite in reply["citations"])
    app.button(key="blood_demo").click().run()
    next(box for box in app.checkbox if box.key and box.key.startswith("blood_check_")).check().run()
    next(button for button in app.button if button.label == "Use verified report in chat").click().run()
    assert not app.exception
    assert app.selectbox(key="source_lab").value.startswith("Reviewed: Synthetic")
from mediguide.lab_review import parse_rows, compare, diet_notes, DEMO
from mediguide.rag import RAGService


def test_bmi_exact_units_and_ambiguous_height():
    assert bmi_value(55, 160) == pytest.approx(21.484375)
    assert "21.5" in bmi_chat("BMI 55 kg 160 cm age 22", [])["answer"]
    assert "21.5" in bmi_chat("BMI 55 kg 1.60 m age 22", [])["answer"]
    assert "21.5" in bmi_chat("BMI 55 kg 5 ft 3 in age 22", [])["answer"]
    assert bmi_chat("for weight 55 kg and 5,3 height", [])["abstained"]
    assert bmi_chat("BMI 55 kg 5 ft 14 in", [])["abstained"]


@pytest.mark.parametrize("weight,height", [(0,160),(55,0),(-55,160),(float('nan'),160),(55,float('inf'))])
def test_bmi_invalid(weight,height):
    with pytest.raises(ValueError):
        bmi_value(weight,height)


def test_bmi_age_pregnancy_and_boundary():
    assert "no adult category" in bmi_answer(55,160,16)["answer"]
    assert "What is your age" in bmi_answer(55,160)["answer"]
    assert "does not classify" in bmi_answer(55,160,25,True)["answer"]
    assert "overweight range" in bmi_answer(100,200,22)["answer"]


def test_bmi_followup():
    assert "healthy-weight range" in bmi_chat("22", [{"role":"user","content":"BMI for 55 kg 160 cm"}])["answer"]


def test_compact_bmi_conversation_routes_before_retrieval():
    from mediguide.rag import RAGService

    service = RAGService("medical")
    question = "healthy bmi range"
    assert "18.5 to below 25" in service.ask(question)["answer"]
    measurements = "90kg and 5feet 6 inches"
    result = service.ask(measurements, [{"role": "user", "content": question}])
    assert "32.0" in result["answer"]
    assert "What is your age" in result["answer"]
    assert result["citations"][0]["source"] == "CDC adult BMI categories"
    result = service.ask("22", [{"role": "user", "content": measurements}])
    assert "obesity range" in result["answer"]


def test_cut_first_aid_not_prescription():
    result = cut_answer("I got a cut from scissors, which medicine should I apply and take?")
    assert "rinse" in result["answer"] and "cannot choose" in result["answer"]
    assert "tetanus" in result["answer"] and result["citations"]
    assert cut_answer("deep cut with something stuck")["emergency"]
    assert cut_answer("How to cut calories?") is None


def test_report_ranges_and_no_deficiency_diagnosis():
    rows, rejected = parse_rows(DEMO, 3)
    assert len(rows) == 3 and not rejected
    assert rows[0]["status"] == "Below supplied range"
    assert rows[1]["status"] == "Within supplied range"
    assert all(r["page"] == 3 for r in rows)
    notes = " ".join(text for text, _ in diet_notes(rows))
    assert "does not by itself establish iron deficiency" in notes
    assert "lentils" in notes and "fortified" in notes


@pytest.mark.parametrize("text", ["Hemoglobin 11.2 g/dL", "Hemoglobin <11 g/dL reference 12-16", "Hemoglobin 11.2 g/dL reference 16-12", "Glucose 90 mg/dL reference 4-6 mmol/L"])
def test_incomplete_or_mixed_unit_rows_rejected(text):
    rows, rejected = parse_rows(text,1)
    assert not rows and rejected


def test_range_boundaries_and_white_cells_no_food_cure():
    assert compare(12,12,16) == "Within supplied range"
    notes = diet_notes([{"test":"WBC","status":"Below supplied range"}])
    assert "not automatically" in notes[0][0]


def test_routing_and_emergency_precedence():
    assert "21.5" in RAGService("medical").ask("BMI for 55 kg 160 cm age 22")["answer"]
    assert RAGService("medical").ask("cut with severe bleeding")["emergency"]
    result = RAGService("medical").ask("What can I do for a common cold?")
    assert "Antibiotics do not treat" in result["answer"]
    assert "calculated BMI" not in RAGService("insurance").ask("BMI for 55 kg 160 cm")["answer"]


def test_bmi_and_lab_ui():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.button(key="nav_Medical knowledge").click().run()
    app.button(key="calculate_bmi").click().run()
    assert not app.exception
    assert any("21.5" in m.value for m in app.markdown)
    app.button(key="nav_Lab report explainer").click().run()
    app.button(key="blood_demo").click().run()
    assert not app.exception
    next(c for c in app.checkbox if str(c.key).startswith("blood_check_")).check().run()
    assert not app.exception
    assert app.dataframe


def test_real_pdf_upload_review_and_invalidation():
    import pymupdf
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((40,60), "Hemoglobin 11.2 g/dL reference 12.0-16.0")
        data = doc.tobytes()
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.button(key="nav_Lab report explainer").click().run()
    app.file_uploader(key="blood_upload").upload("synthetic-blood.pdf", data, "application/pdf").run()
    app.button(key="read_blood").click().run()
    assert not app.exception
    assert "Hemoglobin" in app.session_state["blood_pages"][0]["original"]
    next(c for c in app.checkbox if str(c.key).startswith("blood_check_")).check().run()
    assert app.dataframe
    next(t for t in app.text_area if str(t.key).startswith("blood_text_")).set_value("Hemoglobin 15 g/dL reference 12-16").run()
    assert not any(c.value for c in app.checkbox if str(c.key).startswith("blood_check_"))
    assert not app.dataframe
