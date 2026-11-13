from mediguide.documents import chunk_pages
from mediguide.vectorstore import VectorStore
from mediguide.rag import RAGService
from mediguide.llm import ExtractiveLLM


def test_unrelated_question_returns_no_evidence(tmp_path):
    store = VectorStore("insurance", tmp_path)
    store.add(chunk_pages([(1, "The waiting period for the policy is twenty four months.")], "policy.pdf", "insurance"))
    assert store.search("Explain orbital mechanics") == []
    assert store.search("waiting period")[0].chunk.page == 1


def test_source_selection_prevents_cross_policy_answers(tmp_path):
    store = VectorStore("insurance", tmp_path)
    for name, months in [("a.pdf", "six"), ("b.pdf", "twelve")]:
        store.add(chunk_pages([(1, f"The policy waiting period is {months} months.")], name, "insurance"))
    matches = store.search("waiting period", source="a.pdf")
    assert matches and all(r.chunk.source == "a.pdf" for r in matches)


def test_short_lab_values_are_preserved():
    chunks = chunk_pages([(1, "Hb: 11.2 g/dL")], "lab.pdf", "lab")
    assert chunks[0].text == "Hb: 11.2 g/dL"


def test_replacing_policy_removes_old_terms(tmp_path):
    store = VectorStore("insurance", tmp_path)
    store.replace_source(chunk_pages([(1, "Waiting period is six months.")], "policy.pdf", "insurance"))
    store.replace_source(chunk_pages([(1, "Waiting period is twelve months.")], "policy.pdf", "insurance"))
    assert all("six" not in c.text for c in store.chunks)
    assert len(store.chunks) == 1


def test_history_resolves_followup(tmp_path):
    store = VectorStore("medical", tmp_path)
    store.add(chunk_pages([(1, "Asthma affects the airways. Asthma symptoms include wheezing.")], "source.pdf", "medical"))
    service = object.__new__(RAGService)
    service.route, service.store, service.llm = "medical", store, ExtractiveLLM()
    result = service.ask("What are its symptoms?", [{"role":"user", "content":"What is asthma?"}])
    assert "wheezing" in result["answer"]
