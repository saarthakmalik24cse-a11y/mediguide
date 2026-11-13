"""Distinguish dietary requirements from prescribed treatment doses."""
import re
from .questions import is_medical_dose_question, normalize_question

IRON_URL = "https://ods.od.nih.gov/factsheets/Iron-Consumer/"


def dosage_response(question, source=None):
    question = normalize_question(question)
    if not is_medical_dose_question(question):
        return None
    if source:
        return None  # A selected document is handled by the evidence filter in RAG.
    if re.search(r"\biron\b", question, re.I):
        answer = (
            "**Do you mean daily dietary iron or an iron supplement dose for treatment?** These are different.\n\n"
            "For general **dietary intake**, NIH lists these daily amounts (food plus supplements): [S1]\n\n"
            "| Group | Daily iron requirement |\n|---|---|\n"
            "| Men, 19–50 | 8 mg |\n| Women, 19–50 | 18 mg |\n"
            "| Adults, 51+ | 8 mg |\n| Pregnancy | 27 mg |\n\n"
            "These are nutritional requirements, **not a prescribed supplement dose**. "
            "For a treatment dose, select your prescription or ask your clinician/pharmacist.\n\n"
            "**Food options:** meat, seafood, lentils, beans, and iron-fortified cereals. "
            "Vitamin-C-containing foods help absorption of plant iron. [S1]\n\n"
            "What is your age group, and are you asking about diet or treatment?"
        )
        if re.search(r"\b(older|elderly|seniors?|old|51\+|[6-9]\d)\b", question, re.I):
            answer = (
                "**For adults aged 51 and over, the NIH recommended dietary iron intake is 8 mg per day.** "
                "This is total dietary intake, **not a prescribed supplement dose**. [S1]\n\n"
                "**What you can do:** include iron-containing foods such as beans, lentils, fortified cereals, "
                "meat or seafood. Vitamin-C-containing foods help your body absorb plant iron. [S1]\n\n"
                "**If you mean treatment for low iron/anemia:** a personal tablet dose cannot be determined "
                "from age alone. Ask your clinician/pharmacist to review your results, prescription and other medicines. "
                "Too much supplemental iron can be harmful and can interact with medicines. [S1]\n\n"
                "Are you asking about food intake or a prescribed iron supplement?"
            )
        citations = [{"label":"S1", "source":"NIH Office of Dietary Supplements — Iron", "page":0,
                      "url":IRON_URL, "retrieved_at":"2026-11-11", "score":1.0,
                      "excerpt":"NIH dietary reference amounts: men 19–50: 8 mg; women 19–50: 18 mg; adults 51+: 8 mg; pregnancy: 27 mg. These are dietary requirements, not treatment instructions. Iron-rich foods include meat, seafood, lentils, beans and fortified cereals; vitamin C improves plant-iron absorption. Excess supplemental iron can be harmful and can interact with medicines."}]
        return {"answer":answer,"citations":citations,"results":[],"emergency":False,"abstained":False,"notice":"General dietary reference; no personal treatment dose has been calculated."}
    return {"answer":"To answer a dose question accurately, I need the exact medicine, strength/formulation, and whether you want the instructions from a prescription or general product-label information. Select the relevant prescription/document under Search within. I cannot determine your personal daily dose from a general topic match.",
            "citations":[],"results":[],"emergency":False,"abstained":True,"notice":""}
