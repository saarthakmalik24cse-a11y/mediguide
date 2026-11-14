"""Small auditable output checks; these do not establish clinical correctness."""
import re


def check_answer(answer, results):
    """Reject missing/invalid citations and numbers absent from cited evidence.

    Checking source numbers catches some inventions, but does not verify units,
    negation, entailment or whether a number applies to the patient.
    """
    labels = re.findall(r"\[S(\d+)\]", answer)
    if not labels or any(not 1 <= int(n) <= len(results) for n in labels):
        return False
    evidence = " ".join(results[int(n)-1].chunk.text for n in labels)
    # Remove citation indexes and Markdown numbered-list markers before checking.
    body = re.sub(r"\[S\d+\]", "", answer)
    body = re.sub(r"(?m)^\s*\d+[.)]\s+", "", body)
    numbers = lambda value: set(re.findall(r"(?<!\w)\d+(?:\.\d+)?", value))
    return numbers(body) <= numbers(evidence)
