import json
import re
import csv
from pathlib import Path

from .rag import RAGService


def evaluate_cases(path: Path, k: int = 5) -> tuple[list[dict], dict]:
    if k < 1:
        raise ValueError("K must be positive")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            cases = list(csv.DictReader(handle))
        for case in cases:
            case["relevant_sources"] = [s.strip() for s in case["relevant_sources"].split(";") if s.strip()]
            case["unanswerable"] = case.get("unanswerable", "").lower() == "true"
    else:
        cases = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        result = RAGService(case["route"]).ask(case["question"], k=k)
        retrieved = [f"{r.chunk.source}#p{r.chunk.page}" for r in result["results"]]
        relevant = set(case["relevant_sources"])
        hits = len(set(retrieved) & relevant)
        cited = set(re.findall(r"\[S(\d+)\]", result["answer"]))
        valid = sum(1 for n in cited if 1 <= int(n) <= len(retrieved))
        correct = sum(1 for n in cited if 1 <= int(n) <= len(retrieved) and retrieved[int(n)-1] in relevant)
        unanswerable = case.get("unanswerable", False)
        rows.append({
            "id": case["id"], "question": case["question"], "route": case["route"],
            "precision_at_k": hits / k if not unanswerable else None,
            "recall_at_k": hits / len(relevant) if relevant else None,
            "hit_rate": float(hits > 0) if not unanswerable else None,
            "citation_accuracy": correct / max(1, len(cited)) if not unanswerable else None,
            "citation_validity": valid / len(cited) if cited else None,
            "abstention_correct": float(result.get("abstained", False)) if unanswerable else None,
            "retrieved": retrieved,
        })
    keys = ["precision_at_k", "recall_at_k", "hit_rate", "citation_accuracy", "citation_validity", "abstention_correct"]
    summary = {}
    for key in keys:
        values = [row[key] for row in rows if row[key] is not None]
        summary[key] = sum(values) / len(values) if values else None
    summary.update({"cases": len(rows), "k": k})
    return rows, summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows, summary = evaluate_cases(args.path, args.k)
    payload = json.dumps({"summary": summary, "cases": rows}, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(json.dumps(summary, indent=2))
