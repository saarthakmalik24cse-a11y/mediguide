"""Conservative wording normalization, not medical inference or spell guessing."""
import re


def normalize_question(text):
    replacements = {"oldage": "older adults", "old age people": "older adults",
                    "dosgae": "dosage", "doasge": "dosage", "requrement": "requirement",
                    "haemoglobin": "hemoglobin", "anaemia": "anemia"}
    for original, replacement in replacements.items():
        text = re.sub(r"\b" + re.escape(original) + r"\b", replacement, text, flags=re.I)
    return text.strip()


def is_dose_question(text):
    return bool(re.search(r"\b(doses?|dosage|dosing|daily intake|daily (?:iron )?requirements?|"
                          r"how much|how many.*(?:tablets?|pills?)|kitna|kitni)\b", text, re.I))


def is_medical_dose_question(text):
    # 'How much is the claim?' is not a medicine-dose request.
    return is_dose_question(text) and bool(re.search(
        r"\b(doses?|dosage|dosing|intake|iron|medicine|medication|supplements?|"
        r"tablets?|pills?|take|mg|mcg|insulin|metformin|vitamin)\b", text, re.I))
