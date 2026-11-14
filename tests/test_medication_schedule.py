from mediguide.medication_schedule import build_draft, DEMO


def test_explicit_instructions_and_missing_details():
    draft = build_draft([("demo.pdf", 2, DEMO)])
    a, b = draft["instructions"]
    assert a["timing"] == "morning"
    assert a["page"] == 2
    assert b["timing"] == "Not stated — confirm"
    assert b["frequency"] == "BD"
    assert any("Shorthand" in issue for issue in b["issues"])


def test_never_infers_dose_or_clock_times():
    row = build_draft([("a", 1, "Medicine: Demo 500 mg | Frequency: twice daily")])["instructions"][0]
    assert row["dose"] == "Not stated — confirm"
    assert row["timing"] == "Not stated — confirm"


def test_keeps_duplicates_separate_and_preserves_unparsed_text():
    pages = [("a", 1, "Medicine: Demo | Dose: 1 tablet"), ("b", 3, "Medicine: Demo | Dose: 2 tablets"), ("c", 1, "Unlabelled handwritten content")]
    draft = build_draft(pages)
    assert len(draft["instructions"]) == 2
    assert all(any("Repeated medicine" in issue for issue in row["issues"]) for row in draft["instructions"])
    assert draft["source_pages"][2]["text"] == pages[2][2]


def test_multiline_and_duplicate_labels():
    row = build_draft([("a", 1, "Medicine: Demo\nDose: 1 tablet\nDose: 2 tablets\nTiming: after breakfast")])["instructions"][0]
    assert row["dose"] == "1 tablet / 2 tablets"
    assert any("Repeated dose" in issue for issue in row["issues"])


def test_schedule_screen_demo():
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.button(key="nav_schedule").click().run()
    app.button(key="schedule_demo").click().run()
    assert not app.exception
    assert len(app.session_state["schedule_draft"]["instructions"]) == 2
