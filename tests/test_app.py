from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_every_page_survives_reload():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()
    assert not app.exception
    for page in ["Home", "Medical knowledge", "Patient document chat", "Lab report explainer", "Discharge assistant", "Medication information", "Insurance guidance", "Feedback", "Demo readiness", "AI methods lab", "Admin & evaluation"]:
        app.button(key=f"nav_{page}").click().run()
        assert not app.exception, page
        app.run()
        assert not app.exception, f"reload: {page}"


def test_guided_questions_and_feedback(tmp_path, monkeypatch):
    from mediguide import database
    original = database.connect
    monkeypatch.setattr(database, "connect", lambda: original(tmp_path / "test.db"))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    for page in ["Medical knowledge", "Patient document chat", "Lab report explainer", "Discharge assistant", "Medication information", "Insurance guidance"]:
        app.button(key=f"nav_{page}").click().run()
        quick = next(b for b in app.button if b.key and b.key.startswith("quick_"))
        quick.click().run()
        assert not app.exception, page
        assert len(app.chat_message) >= 2, page
        assert any("[S" in m.value for m in app.markdown), page
    app.button(key="nav_Feedback").click().run()
    next(b for b in app.button if b.label == "Submit feedback").click().run()
    assert not app.exception
    assert app.success


def test_policy_checklist_and_evaluation_persist():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.button(key="nav_Insurance guidance").click().run()
    app.selectbox(key="source_insurance").select("synthetic_insurance_policy.pdf").run()
    next(b for b in app.button if b.label == "Extract requirements from selected policy").click().run()
    assert not app.exception
    assert "policy_checklist" in app.session_state
    app.button(key="nav_Admin & evaluation").click().run()
    next(b for b in app.button if b.label == "Run evaluation").click().run()
    assert not app.exception
    app.run()
    assert len(app.metric) == 4


def test_ai_lab_plans_and_detects_impossible_schedule():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.button(key="nav_AI methods lab").click().run()
    next(b for b in app.button if b.label == "Find preparation plan").click().run()
    assert not app.exception
    assert app.session_state["search_demo"]["cost"] == 4
    next(b for b in app.button if b.label == "Build feasible schedule").click().run()
    assert app.session_state["csp_demo"]["assignment"] is not None
    next(s for s in app.slider if s.label == "Submission deadline (day number)").set_value(1).run()
    next(b for b in app.button if b.label == "Build feasible schedule").click().run()
    assert not app.exception
    assert app.session_state["csp_demo"]["assignment"] is None


def test_actual_chat_iron_question(tmp_path, monkeypatch):
    from mediguide import database
    original = database.connect
    monkeypatch.setattr(database, "connect", lambda: original(tmp_path / "test.db"))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.button(key="nav_Medical knowledge").click().run()
    app.chat_input(key="chat_medical").set_value("how much dosage of iron is require for oldage people").run()
    assert not app.exception
    answer = app.session_state["messages"]["medical:All sources"][-1]["content"]
    assert "8 mg per day" in answer
    assert "dehydration" not in answer.lower()


def test_answer_survives_history_storage_failure(monkeypatch):
    from mediguide import database
    def unavailable(*args, **kwargs):
        raise OSError("Simulated storage failure")
    monkeypatch.setattr(database, "save_message", unavailable)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.button(key="nav_Medical knowledge").click().run()
    app.chat_input(key="chat_medical").set_value("daily iron requirement for seniors").run()
    assert not app.exception
    assert any("could not be saved" in warning.value for warning in app.warning)
    assert "8 mg per day" in app.session_state["messages"]["medical:All sources"][-1]["content"]


def test_demo_readiness_page():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.button(key="nav_Demo readiness").click().run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 6
