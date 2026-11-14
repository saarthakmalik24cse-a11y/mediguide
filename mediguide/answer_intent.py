"""Conservative sentence-level answerability; topic overlap alone is insufficient."""
import re


def matches_intent(question: str, sentence: str) -> bool:
    q, s = question.lower(), sentence.lower()
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
