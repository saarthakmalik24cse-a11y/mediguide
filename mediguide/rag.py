from .config import settings
from .llm import get_llm
from .safety import emergency_message
from .vectorstore import VectorStore
from .llm import ExtractiveLLM
import re
import requests
from .dosage import dosage_response
from .questions import normalize_question, is_medical_dose_question
from .answer_checks import check_answer
from .answer_intent import evidence_sentences


class RAGService:
    def __init__(self, route: str):
        self.route = route
        self.store = VectorStore(route)
        self.llm = get_llm()

    def ask(self, question: str, history: list[dict] | None = None, k: int | None = None, source: str | None = None) -> dict:
        question = normalize_question(question)
        if not question or len(question) > 2000:
            return {"answer": "Please ask one focused question between 1 and 2,000 characters.",
                    "citations": [], "results": [], "emergency": False, "abstained": True, "notice": ""}
        urgent = emergency_message(question)
        if urgent:
            return {"answer": urgent, "citations": [], "results": [], "emergency": True}
        if self.route == "medical" and source is None:
            from .health_tools import bmi_chat, cut_answer
            from .common_health import common_answer
            for response in (bmi_chat(question, history or []), cut_answer(question), common_answer(question)):
                if response is not None:
                    return response
        if not source and self.route in {"patient", "lab", "discharge", "insurance"}:
            sources = {chunk.source for chunk in self.store.chunks}
            if len(sources) > 1:
                return {"answer": "Please choose one document under Choose your sources → Search within. Multiple documents are available; I should not combine different patient records or policy versions.",
                        "citations": [], "results": [], "emergency": False, "abstained": True, "notice": "Select the document you want this answer to use."}
        dose_answer = dosage_response(question, source)
        if dose_answer and self.route != "insurance":
            return dose_answer
        retrieval_query = question
        if history and re.search(r"\b(it|that|this|these|those|its)\b", question, re.I):
            previous = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
            retrieval_query = previous + " " + question
        results = self.store.search(retrieval_query, k or settings.top_k, source=source)
        if self.route != "insurance" and is_medical_dose_question(question):
            results = [r for r in results if re.search(r"\b\d+(?:\.\d+)?\s*(mg|mcg|ml|units|tablets?)\b", r.chunk.text, re.I)
                       and re.search(r"\b(dose|dosage|daily|twice|once|every|take|administer)\b", r.chunk.text, re.I)]
        notice = ""
        if not results:
            answer = "I could not find enough relevant evidence in the selected sources. Try a more specific question or upload a document that covers it."
        else:
            try:
                answer = self.llm.answer(retrieval_query, results, history or [], self.route)
            except (requests.RequestException, KeyError, IndexError, ValueError):
                answer = ExtractiveLLM().answer(retrieval_query, results, [], self.route)
                notice = "The language service is unavailable; showing source excerpts instead."
            if not isinstance(self.llm, ExtractiveLLM) and not check_answer(answer, results):
                answer = ExtractiveLLM().answer(retrieval_query, results, [], self.route)
                notice = "Showing source excerpts because generated citations or numbers could not be verified against the cited evidence."
        citations = [{"label": f"S{i}", "source": r.chunk.source, "page": r.chunk.page,
                      "score": round(r.score, 3), "excerpt": r.chunk.text,
                      "url": r.chunk.metadata.get("url"), "retrieved_at": r.chunk.metadata.get("retrieved_at")}
                     for i, r in enumerate(results, 1)]
        used_labels = set(re.findall(r"\[(S\d+)\]", answer))
        citations = [c for c in citations if c["label"] in used_labels]
        for citation in citations:
            citation["supporting_quotes"] = evidence_sentences(answer, citation["label"], citation["excerpt"])
        return {"answer": answer, "citations": citations, "results": results, "emergency": False,
                "abstained": not citations, "notice": notice}
