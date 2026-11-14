"""Conservative sentence-level answerability; topic overlap alone is insufficient."""
import re


MEDICINE_USE = re.compile(r"\b(?:used for|why (?:is|are) .+ used|uses? of|what (?:does|do) .+ (?:do|treat|help with)|purpose of)\b", re.I)
MEDICINE_PURPOSE_EVIDENCE = re.compile(r"\b(?:indications?|indicated|purpose|uses?|used to|used for|treat\w*|reliev\w*|reduc\w*)\b", re.I)
WARNING_SECTION = re.compile(r"^\s*(?:(?:liver|boxed|black box) )?warnings?\b|\b(?:severe liver damage|allergy alert)\b", re.I)


def medicine_overview(question: str) -> dict | None:
    """Answer verified ingredient-level facts for simple questions only."""
    from .health_tools import sourced

    medicine = r"(?:paracetamol|acetaminophen)"
    q = question.strip().lower().rstrip("?.!")
    patterns = (
        rf"(?:what is|define|explain|tell me about) {medicine}",
        rf"(?:what is {medicine} used for|why is {medicine} used|what does {medicine} (?:do|treat)|(?:uses?|purpose) of {medicine})",
    )
    if not any(re.fullmatch(pattern, q) for pattern in patterns):
        return None
    return sourced(
        "**Paracetamol (also called acetaminophen)** is a medicine used to relieve pain and reduce fever.",
        "FDA: Acetaminophen",
        "https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen",
        "The FDA identifies paracetamol as another name for acetaminophen, an ingredient used for pain relief and fever reduction.",
    )


def matches_intent(question: str, sentence: str) -> bool:
    q, s = question.lower(), sentence.lower()
    if MEDICINE_USE.search(q) and not re.search(r"\b(?:warnings?|side effects?|risks?)\b", q):
        return bool(MEDICINE_PURPOSE_EVIDENCE.search(s) and not WARNING_SECTION.search(s))
    rules = [
        (r"\b(symptoms?|signs?)\b", r"\b(symptoms?|signs?|wheez|pain|cough|fever|fatigue|tired|breath)"),
        (r"\b(side effects?|adverse|warnings?|precautions?)\b", r"\b(side effects?|adverse|warning|avoid|risk|contraindicat|do not|should not)"),
        (r"\b(causes?|why)\b", r"\b(caus|because|due to|results? from|risk factors?)"),
        (r"\b(treat|treatment|manage|management|prevent|solutions?)\b", r"\b(treat|manage|prevent|exercise|physical activity|diet|avoid|recommend|can help)"),
        (r"\b(dosage|dosing|dose)\b", r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|ml|units?|tablets?)\b"),
        (r"\b(when|deadline|waiting period|how long)\b", r"\b(days?|weeks?|months?|years?|hours?|follow.up|before|after|within|deadline|waiting)\b"),
    ]
    triggered = [pattern for intent, pattern in rules if re.search(intent, q)]
    return not triggered or any(re.search(pattern, s) for pattern in triggered)


def evidence_sentences(answer: str, label: str, text: str) -> list[str]:
    """Highlight only verbatim matches, not inferred support for generated claims."""
    normalized = " ".join(text.split())
    found = []
    for part in re.split(r"\n+", answer):
        if f"[{label}]" not in part:
            continue
        part = re.sub(r"\[S\d+\]", "", part).strip(" -*\n")
        if len(part) > 12 and part in normalized:
            found.append(part)
    return found
