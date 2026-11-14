"""Deterministic BMI and sourced first-aid cards, independent of an LLM."""
import math
import re
from .models import Chunk, SearchResult

BMI_URL = "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
CUT_URL = "https://www.nhs.uk/conditions/cuts-and-grazes/"


def sourced(answer: str, title: str, url: str, evidence: str, urgent: bool = False) -> dict:
    chunk = Chunk("health-tool-" + title, evidence, title, 0, "medical",
                  {"url": url, "retrieved_at": "2026-11-14", "kind": "authored_source_summary"})
    return {"answer": answer + " [S1]", "citations": [{"label": "S1", "source": title,
             "page": 0, "excerpt": evidence, "url": url, "retrieved_at": "2026-11-14"}],
            "results": [SearchResult(chunk, 1.0)], "emergency": urgent, "abstained": False,
            "notice": "Source-based educational summary; not an individual diagnosis."}


def clarify(text: str) -> dict:
    return {"answer": text, "citations": [], "results": [], "emergency": False, "abstained": True, "notice": ""}


def bmi_value(weight_kg: float, height_cm: float) -> float:
    if not all(math.isfinite(v) for v in (weight_kg, height_cm)) or not 10 <= weight_kg <= 500 or not 50 <= height_cm <= 250:
        raise ValueError("Check units: supported input is 10–500 kg and 50–250 cm.")
    return weight_kg / (height_cm / 100) ** 2


def bmi_answer(weight: float, cm: float, age: int | None = None, pregnant: bool = False) -> dict:
    value = bmi_value(weight, cm)
    answer = f"Your calculated BMI is **{value:.1f} kg/m²**. Calculation: {weight:g} kg ÷ ({cm / 100:g} m × {cm / 100:g} m)."
    if pregnant:
        answer += " Pregnancy needs a clinician's assessment; this tool does not classify pregnancy weight."
    elif age is None:
        answer += " What is your age? Adult categories below apply only from age 20."
    elif age < 20:
        answer += " For someone under 20, use an age- and sex-specific BMI-for-age assessment; no adult category is assigned."
    else:
        category = "underweight" if value < 18.5 else "healthy-weight range" if value < 25 else "overweight range" if value < 30 else "obesity range"
        answer += f" For adults aged 20+, this falls in the **{category}**. BMI is a screening measure, not proof that someone is healthy or unhealthy."
    return sourced(answer, "CDC adult BMI categories", BMI_URL,
                   "BMI = weight in kilograms divided by height in metres squared. Adult categories from age 20: below 18.5 underweight; 18.5 to below 25 healthy weight; 25 to below 30 overweight; 30 or higher obesity. BMI is one screening measure, not a diagnosis.")


def bmi_chat(question: str, history: list[dict]) -> dict | None:
    previous = next((m["content"] for m in reversed(history) if m.get("role") == "user"), "")
    q = question.lower()
    if not (re.search(r"\bbmi\b|body mass index", q) or (re.search(r"\bkg\b", q) and re.search(r"height|cm|feet|ft|inches|\d['′]", q))):
        if not (re.search(r"\bbmi\b|\bkg\b", previous.lower()) and re.fullmatch(r"(?:i am |age[: ]*)?\d{1,3}(?: years? old)?[.!]?", q)):
            return None
        q = previous.lower() + " age " + re.search(r"\d+", q).group()
    if re.search(r"\d\s*[,\.]\s*\d\s*(?:height|feet|ft)", q):
        return clarify("Does 5,3 / 5.3 mean 5 feet 3 inches or decimal feet? Write height as 160 cm or 5 ft 3 in, plus weight in kg and age.")
    weight = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\b", q)
    metric = re.search(r"(\d+(?:\.\d+)?)\s*(cm|centimeters?|metres?|meters?|m)\b", q)
    imperial = re.search(r"(\d+)\s*(?:ft|feet|foot|['′])\s*(\d{1,2})?\s*(?:inches|inch|in|[\"″])?", q)
    age_match = re.search(r"(?:age[d]?\s*[:=]?\s*|i am\s+)(\d{1,3})\b|(\d{1,3})\s*(?:years? old|yo)\b", q)
    age = int(next(g for g in age_match.groups() if g)) if age_match else None
    if not weight or not (metric or imperial):
        return clarify("Please give weight, height with units, and age—for example: BMI for 55 kg, 160 cm, age 22. You can also use the BMI calculator on this page.")
    if metric:
        cm = float(metric.group(1)) * (1 if metric.group(2).startswith("c") else 100)
    else:
        inches = int(imperial.group(2) or 0)
        if inches >= 12:
            return clarify("The inches part must be below 12. Please check your height.")
        cm = (int(imperial.group(1)) * 12 + inches) * 2.54
    try:
        return bmi_answer(float(weight.group(1)), cm, age, "pregnan" in q)
    except ValueError as exc:
        return clarify(str(exc))


def cut_answer(question: str) -> dict | None:
    q = question.lower()
    if not re.search(r"\b(cut|cuts|scissors?|graze|grazes|wound)\b", q) or re.search(r"cut (?:down|weight|calories|sugar)|haircut", q):
        return None
    urgent = bool(re.search(r"won.t stop|cannot stop|can.t stop|spurting|deep|numb|can.t move|cannot move|stuck|gaping", q))
    if urgent:
        text = "Seek urgent in-person care now for a deep wound, uncontrolled bleeding, loss of feeling/movement or an embedded object. Do not remove an embedded object. Apply pressure with a clean cloth, avoiding pressure directly on any embedded object."
    else:
        text = ("For a **small, superficial cut**, first control bleeding with a clean cloth, rinse with clean running water, and cover with a sterile dressing. Keep it clean and change a wet or dirty dressing.\n\n"
                "**Medicine:** I cannot choose an oral antibiotic or antibiotic cream from this description. A clinician decides whether infection treatment or tetanus protection is needed. Ask a pharmacist which pain-relief option is safe for your age, conditions and existing medicines.\n\n"
                "Get urgent care if bleeding will not stop, the wound is deep, something is embedded, or you lose sensation/movement. Increasing redness, swelling, pus or fever needs medical assessment.\n\n"
                "How deep is the cut, has bleeding stopped, were the scissors dirty, and when was your last tetanus vaccination?")
    return sourced(text, "NHS cuts and grazes", CUT_URL,
                   "Minor cuts: control bleeding, rinse with water and cover with a sterile dressing. Persistent bleeding, deep wounds, embedded objects or impaired movement/sensation require emergency assessment. Infection signs need prompt assessment. Clinicians may consider tetanus protection or antibiotics depending on the wound.", urgent)


def render_bmi() -> None:
    import streamlit as st
    with st.expander("Calculate BMI", icon=":material/calculate:"):
        weight = st.number_input("Weight (kg)", 10.0, 500.0, 55.0)
        cm = st.number_input("Height (cm)", 50.0, 250.0, 160.0)
        age = st.number_input("Age (years)", 2, 120, 22)
        pregnant = st.checkbox("Pregnancy applies")
        if st.button("Calculate BMI", key="calculate_bmi"):
            try:
                result = bmi_answer(weight, cm, age, pregnant)
                st.markdown(result["answer"])
                st.link_button("CDC method and categories", BMI_URL)
            except ValueError as exc:
                st.error(str(exc))
