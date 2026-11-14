from mediguide.answer_checks import check_answer
from mediguide.models import Chunk, SearchResult
from mediguide.rag import RAGService
from mediguide.llm import ExtractiveLLM
from mediguide.vectorstore import VectorStore
from mediguide.documents import chunk_pages
import pytest


@pytest.mark.parametrize("answer,valid", [
    ("Waiting period is 24 months. [S1]", True),
    ("Waiting period is 12 months. [S1]", False),
    ("Waiting period is 24 months. [S9]", False),
    ("Waiting period is 24 months.", False),
    ("1. Waiting period is 24 months. [S1]", True),
])
def test_citation_and_number_checks(answer, valid):
    results = [SearchResult(Chunk("a", "Waiting period is 24 months.", "policy.pdf", 2, "insurance", {}), 1)]
    assert check_answer(answer, results) == valid


@pytest.mark.parametrize("route", ["patient", "lab", "discharge", "insurance"])
def test_multiple_private_documents_require_selection(tmp_path, route):
    store = VectorStore(route, tmp_path)
    for name, days in [("a.pdf", 7), ("b.pdf", 14)]:
        store.add(chunk_pages([(1, f"Follow-up is in {days} days.")], name, route))
    service = object.__new__(RAGService)
    service.route, service.store, service.llm = route, store, ExtractiveLLM()
    assert service.ask("When is the follow-up?")["abstained"]
    result = service.ask("When is the follow-up?", source="a.pdf")
    assert "7 days" in result["answer"]
    assert "14 days" not in result["answer"]


@pytest.mark.parametrize("question", ["   ", "x" * 2001])
def test_invalid_question_length(question):
    result = RAGService("medical").ask(question)
    assert result["abstained"]
    assert not result["citations"]
