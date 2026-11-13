import re

EMERGENCY_PATTERNS = [
    r"chest pain", r"cannot breathe", r"can't breathe", r"severe bleeding",
    r"unconscious", r"overdose", r"suicid", r"stroke", r"anaphylaxis",
]


def emergency_message(query: str) -> str | None:
    if any(re.search(pattern, query, re.I) for pattern in EMERGENCY_PATTERNS):
        return ("This may be an emergency. Contact your local emergency service now or go to the nearest "
                "emergency department. Do not wait for an AI response. If safe, stay with the person and "
                "bring their medication list and medical documents.")
    return None


def disclaimer(route: str) -> str:
    if route == "insurance":
        return "Insurance guidance is informational. Coverage decisions come from the insurer and policy contract."
    return "Educational information only—not a diagnosis or a substitute for a licensed clinician."
