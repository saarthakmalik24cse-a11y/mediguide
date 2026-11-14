"""Short authored educational cards. Sources checked 2026-11-14."""
import re
from .health_tools import sourced

CARDS = {
    "cold": (r"\b(common cold|cold|runny nose|sneez\w*)\b", "NHS common cold", "https://www.nhs.uk/conditions/common-cold/",
             "A common cold is a viral illness, often causing a runny or blocked nose, sneezing, sore throat and cough. Rest, fluids and regular healthy food can help you feel better. Antibiotics do not treat cold viruses. Seek medical advice for worsening symptoms, prolonged fever or symptoms that do not improve; breathing difficulty or chest pain needs urgent assessment. Ask a pharmacist about suitable symptom relief rather than combining cold medicines yourself."),
    "headache": (r"\bheadaches?\b", "NHS headaches", "https://www.nhs.uk/symptoms/headaches/",
                 "Headache is a symptom with many possible causes. For a mild headache, try water, regular meals, rest and reducing eye strain. Repeated or worsening headaches need medical review. A sudden extremely painful headache, weakness, confusion, a seizure, vision loss, or fever with stiff neck requires emergency assessment. These general measures do not identify the cause of your headache."),
    "diarrhoea": (r"\b(diarrh[oe]+a|diarrhea|loose stools?|loose motions?)\b", "NHS diarrhoea and vomiting", "https://www.nhs.uk/symptoms/diarrhoea-and-vomiting/",
                  "Diarrhoea means frequent loose or watery stools. Rest and take frequent small sips of fluid; a pharmacist can advise on oral rehydration products. Eat when able. Seek medical advice if you cannot keep fluids down, pass blood or show dehydration; severe sudden abdominal pain or blood in vomit needs emergency care. Children, older adults and people with other health conditions need extra caution. Do not automatically take antibiotics or anti-diarrhoea medicines."),
}


def common_answer(question: str) -> dict | None:
    q = question.lower()
    if re.search(r"(?:basic|common) (?:illness|illnesses|diseases|health problems)", q):
        return sourced("Examples of common health problems include colds, headaches and diarrhoea. Ask about one—for example, 'What can I do for a common cold?'—to see basic care and warning signs. Symptoms can have different causes; this list does not diagnose you.", "NHS common cold", CARDS["cold"][2], CARDS["cold"][3])
    for pattern, title, url, text in CARDS.values():
        if re.search(pattern, q):
            # Only general symptom/care questions, not unsupported specialised claims.
            if re.search(r"\b(dose|dosage|pregnan|baby|infant|child|cancer|surgery|vaccine)\b", q):
                return None
            urgent = bool(re.search(r"sudden|worst|stiff neck|confus|seizure|vision loss|blood in vomit", q))
            if urgent:
                text = "Your described warning signs need urgent in-person assessment; do not rely on self-care advice. " + text
            return sourced(text, title, url, text, urgent)
    return None
