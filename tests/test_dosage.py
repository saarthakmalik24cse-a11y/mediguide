from mediguide.dosage import dosage_response


def test_iron_question_distinguishes_diet_from_treatment():
    answer = dosage_response("what is the daily dosage of iron")
    assert "not a prescribed supplement dose" in answer["answer"]
    assert "18 mg" in answer["answer"]
    assert answer["citations"][0]["url"].startswith("https://ods.od.nih.gov/")


def test_unknown_dosage_requests_context():
    assert dosage_response("What dose of metformin should I take?")["abstained"]
    assert dosage_response("What is diabetes?") is None
