"""Answer-level checks across routes; not a clinical validation study."""
import pytest
from mediguide.documents import chunk_pages
from mediguide.vectorstore import VectorStore
from mediguide.rag import RAGService
from mediguide.llm import ExtractiveLLM


@pytest.mark.parametrize("question", [
    "how much dosage of iron is require for oldage people",
    "How much iron do elderly people need?",
    "daily iron requirement for seniors",
    "iron dosgae for older adults",
    "How much iron should a 70 year old take?",
])
def test_older_iron_variations(question):
    result = RAGService("medical").ask(question)
    assert "8 mg per day" in result["answer"]
    assert "not a prescribed supplement dose" in result["answer"]
    assert "dehydration" not in result["answer"].lower()
    assert "blood count" not in result["answer"].lower()
    assert result["citations"][0]["url"].startswith("https://ods.od.nih.gov/")


CASES = [
    ("medical", "What is asthma?", "Asthma affects the airways and can cause wheezing.", "airways", False),
    ("medical", "What is my potassium value?", "Asthma affects the airways and can cause wheezing.", None, True),
    ("patient", "When is the follow-up?", "Follow-up is scheduled in 7 days.", "7 days", False),
    ("patient", "What is my glucose value?", "Follow-up is scheduled in 7 days.", None, True),
    ("lab", "What is my hemoglobin?", "Hemoglobin: 11.2 g/dL; reference range 12.0–16.0 g/dL.", "11.2 g/dL", False),
    ("lab", "What is my troponin?", "Hemoglobin: 11.2 g/dL; reference range 12.0–16.0 g/dL.", None, True),
    ("discharge", "When is the follow-up?", "Follow-up is required in 3 days at the clinic.", "3 days", False),
    ("discharge", "What is my cholesterol value?", "Follow-up is required in 3 days at the clinic.", None, True),
    ("medication", "What dose is written?", "Prescribed dose: take 5 mg once daily as directed.", "5 mg", False),
    ("medication", "What dosage is written?", "This medicine is discussed with your doctor.", None, True),
    ("medication", "What is the metformin dose?", "Amlodipine dose: take 5 mg once daily.", None, True),
    ("insurance", "What is the waiting period?", "The waiting period is 24 months for pre-existing conditions.", "24 months", False),
    ("insurance", "What is the maternity sublimit?", "The waiting period is 24 months for pre-existing conditions.", None, True),
    ("insurance", "What documents for reimbursement?", "For reimbursement submit an itemized bill and discharge summary.", "itemized bill", False),
]


@pytest.mark.parametrize("route,question,evidence,expected,abstain", CASES)
def test_all_routes_against_controlled_evidence(tmp_path, route, question, evidence, expected, abstain):
    store = VectorStore(route, tmp_path)
    store.add(chunk_pages([(2, evidence)], "selected.pdf", route))
    store.add(chunk_pages([(1, "Dehydration can occur in older people. A blood count measures blood cells.")], "distractor.pdf", route))
    service = object.__new__(RAGService)
    service.route, service.store, service.llm = route, store, ExtractiveLLM()
    result = service.ask(question, source="selected.pdf")
    assert result["abstained"] == abstain, result["answer"]
    if expected:
        assert expected in result["answer"]
        assert result["citations"]
        assert all(c["source"] == "selected.pdf" and c["page"] == 2 for c in result["citations"])
    else:
        assert not result["citations"]


def test_unrelated_details_not_added(tmp_path):
    store = VectorStore("medical", tmp_path)
    store.add(chunk_pages([(1, "Asthma affects the airways. Dehydration affects older people.")], "demo.pdf", "medical"))
    service = object.__new__(RAGService)
    service.route, service.store, service.llm = "medical", store, ExtractiveLLM()
    result = service.ask("What is asthma in older people?")
    assert "airways" in result["answer"]
    assert "Dehydration" not in result["answer"]


@pytest.mark.parametrize("route,question,expected,forbidden", [
    ("medical", "What is diabetes?", "glucose", "aplastic"),
    ("medical", "What is anemia?", "anemia", "Aplastic anemia is"),
    ("medication", "What is metformin used for?", "metformin", "Amoxicillin"),
    ("insurance", "What documents are required for reimbursement?", "claim form", "guaranteed approval"),
])
def test_public_and_demo_corpus_regressions(route, question, expected, forbidden):
    result = RAGService(route).ask(question, k=3)
    assert expected in result["answer"]
    assert forbidden not in result["answer"]
    assert result["citations"]
