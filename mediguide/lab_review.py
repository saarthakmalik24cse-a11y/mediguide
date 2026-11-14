"""Conservative lab-row parsing: compare only supplied ranges in matching units."""
import re
import math
import hashlib
import json

LAB_URL = "https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/"
HB_URL = "https://medlineplus.gov/lab-tests/hemoglobin-test/"
IRON_URL = "https://ods.od.nih.gov/factsheets/Iron-Consumer/"
B12_URL = "https://ods.od.nih.gov/factsheets/VitaminB12-Consumer/"
NUMBER = r"\d+(?:\.\d+)?"
ROW = re.compile(rf"^\s*([A-Za-z][A-Za-z0-9 ()/-]*?)\s*[:|]?\s+({NUMBER})\s+([A-Za-zµμ%][A-Za-z0-9µμ%/^.*-]*)\s*[;|,]?\s*(?:reference\s*(?:range)?|normal\s*(?:range)?|range)?\s*[:(]?\s*({NUMBER})\s*[-–]\s*({NUMBER})\s*\)?\s*$", re.I)
DEMO = "Hemoglobin 11.2 g/dL reference 12.0-16.0\nPlatelets 240 x10^9/L reference 150-450\nVitamin B12 180 pg/mL reference 200-900"


def compare(value: float, low: float, high: float) -> str:
    if not all(math.isfinite(v) for v in (value, low, high)) or min(value, low, high) < 0 or low >= high:
        raise ValueError("Values must be finite, non-negative, with a lower bound below the upper bound.")
    return "Below supplied range" if value < low else "Above supplied range" if value > high else "Within supplied range"


def parse_rows(text: str, page: int) -> tuple[list[dict], list[str]]:
    rows, unparsed = [], []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = ROW.fullmatch(line)
        if not match:
            # Also accept the bundled PDF's parenthesized reference and printed flag.
            clean = re.sub(r"\s*\((?:demo\s+)?reference\s+(" + NUMBER + r"\s*[-–]\s*" + NUMBER + r")\)\s*(?:[-–—]\s*flagged\s+(?:low|high))?\.?$", r" reference \1", line, flags=re.I)
            match = ROW.fullmatch(clean)
        if not match:
            unparsed.append(line)
            continue
        name, value, unit, low, high = match.groups()
        try:
            status = compare(float(value), float(low), float(high))
        except ValueError:
            unparsed.append(line)
            continue
        rows.append({"test": name.strip(), "value": float(value), "unit": unit,
                     "lower": float(low), "upper": float(high), "status": status, "page": page, "evidence": line})
    return rows, unparsed


def report_overview(question: str, chunks: list) -> dict | None:
    if not re.search(r"\b(?:explain|summari[sz]e|review|improve|abnormal|out of range|what (?:is|looks) (?:low|high|wrong))\b", question, re.I):
        return None
    if not re.search(r"\b(?:report|results?|values?|improve|abnormal|out of range|what (?:is|looks) (?:low|high|wrong))\b", question, re.I):
        return None
    from .health_tools import clarify
    citations, lines, seen = [], [], set()
    outside = 0
    for chunk in chunks:
        # Join wrapped units and split separate results printed on one PDF line.
        text = re.sub(r"(?<=\d)\n(?=[A-Za-z%µμ][\w^/%.-]*\s*\()", " ", chunk.text)
        text = re.sub(r"(\)\s*(?:[-–—]\s*flagged\s+(?:low|high))?)\.? +(?=[A-Za-z][A-Za-z 0-9/-]*:\s*\d)", r"\1\n", text, flags=re.I)
        rows, _ = parse_rows(text, chunk.page)
        for row in rows:
            key = (chunk.page, row["test"], row["value"], row["unit"], row["lower"], row["upper"])
            if key in seen:
                continue
            seen.add(key)
            label = f"S{len(citations) + 1}"
            citations.append({"label": label, "source": chunk.source, "page": chunk.page,
                              "excerpt": row["evidence"]})
            outside += row["status"] != "Within supplied range"
            lines.append(f"- **{row['test']}**: {row['value']:g} {row['unit']} "
                         f"(report range {row['lower']:g}–{row['upper']:g} {row['unit']}). "
                         f"{row['status']}. [{label}]")
    if not lines:
        return clarify("I couldn't reliably pair results with their printed reference ranges. "
                       "Use Blood-report scan and verify the rows, or ask about a specific test and page.")
    return {"answer": f"**{outside} of {len(lines)} readable results are outside their printed ranges.**\n\n"
                      + "\n".join(lines)
                      + "\n\nReview out-of-range results with the clinician who ordered the report. "
                        "Other rows and formats may need manual review.",
            "citations": citations, "results": [], "emergency": False, "abstained": False, "notice": ""}


def diet_notes(rows: list[dict]) -> list[tuple[str, str]]:
    notes = []
    names = [r["test"].lower() for r in rows if r["status"] == "Below supplied range"]
    if any(re.fullmatch(r"hemoglobin|haemoglobin|hb|hgb|ferritin|serum iron|iron", name) for name in names):
        notes.append(("Low hemoglobin does not by itself establish iron deficiency. Ask your clinician what further evaluation is appropriate; do not start iron solely from this comparison.", HB_URL))
        notes.append(("General iron-food ideas, not a deficiency treatment: lentils/beans, iron-fortified cereals, and meat/seafood if you eat them. Pair plant iron with vitamin-C foods such as citrus or tomatoes. Follow existing dietary restrictions and discuss supplements with your clinician.", IRON_URL))
    if any(re.fullmatch(r"vitamin b12|b12|vitamin b-12", name) for name in names):
        notes.append(("General B12-food ideas: fish, meat, eggs, dairy or foods fortified with B12. Check fortified-food labels. A low result needs clinical interpretation; food alone may not address the cause.", B12_URL))
    if not notes:
        notes.append(("No nutrient-specific diet conclusion can be drawn from these rows. A low blood-cell count is not automatically a dietary deficiency. Discuss abnormal results with the clinician who ordered the test.", LAB_URL))
    return notes


def render_lab_review() -> None:
    import streamlit as st
    from .ocr_review import read_review_pages
    st.subheader("Scan and understand a blood report")
    st.caption("Synthetic/demo PDFs only · review the original before interpreting extracted values.")
    st.warning("This compares the report's own reference intervals. It cannot diagnose a deficiency, choose supplements or declare a report safe. A critical lab flag or severe symptoms needs prompt medical review.")
    upload = st.file_uploader("Blood-report PDF (max 5 MB / 10 pages)", type=["pdf"], key="blood_upload")
    use_ocr = st.checkbox("Scan image-based PDF with OCR", key="blood_ocr")
    fingerprint = hashlib.sha256(upload.getvalue()).hexdigest() if upload else "none"
    if st.session_state.get("blood_fingerprint") != fingerprint:
        st.session_state.pop("blood_pages", None)
        st.session_state.blood_fingerprint = fingerprint
    if st.button("Read blood report", disabled=upload is None, key="read_blood"):
        st.session_state.pop("blood_pages", None)
        try:
            st.session_state.blood_pages = read_review_pages(upload.getvalue(), use_ocr)
            st.session_state.blood_run = st.session_state.get("blood_run", 0) + 1
        except Exception as exc:
            st.error(f"Unable to read report: {exc}")
    if st.button("Try synthetic blood-report example", key="blood_demo"):
        st.session_state.blood_pages = [{"page": 1, "original": DEMO, "image": None}]
        st.session_state.blood_run = st.session_state.get("blood_run", 0) + 1
    pages = st.session_state.get("blood_pages", [])
    all_rows, originals, checked = [], [], []
    for page in pages:
        key = f"{fingerprint}_{st.session_state.get('blood_run', 0)}_{page['page']}"
        with st.expander(f"Review page {page['page']}", expanded=True):
            left, right = st.columns(2)
            with left:
                if page["image"]:
                    st.image(page["image"], alt="Original blood report page for checking values and units")
                st.text(page["original"])
            with right:
                st.caption("Use one row per test: Hemoglobin 11.2 g/dL reference 12.0-16.0. Value and both bounds must use the same printed unit. Missing ranges, multiple age/sex ranges and < or > results need clinician review; do not invent limits.")
                text = st.text_area("Check/correct extracted rows", page["original"], height=200, key="blood_text_" + key)
                rows, unparsed = parse_rows(text, page["page"])
                if unparsed:
                    st.warning(f"{len(unparsed)} lines not interpreted; inspect them for omitted results.")
                    st.text("\n".join(unparsed))
                digest = hashlib.sha256(text.encode()).hexdigest()
                checked.append(st.checkbox("I verified names, values, units and the applicable reference ranges against this page", key="blood_check_" + key + digest))
                all_rows.extend(rows)
                originals.append({"page": page["page"], "original": page["original"], "reviewed": text, "unparsed": unparsed})
    if pages and all(checked):
        if not all_rows:
            st.info("No complete comparable rows found. This does not mean the report is normal.")
            return
        st.dataframe([{k:v for k,v in r.items() if k != "evidence"} for r in all_rows], hide_index=True, alt="Reviewed blood results compared with their supplied reference intervals")
        st.caption("Within range does not exclude illness. Outside range does not prove a nutrient deficiency. No units or laboratory intervals were supplied by the app.")
        st.link_button("How to interpret laboratory ranges", LAB_URL)
        st.subheader("What to discuss next and food information")
        for text, url in diet_notes(all_rows):
            st.write(text)
            st.link_button("Read the supporting reference", url)
        st.download_button("Download reviewed summary", json.dumps({"status":"User-reviewed range comparison; not a diagnosis", "rows":all_rows,"pages":originals,"diet_notes":diet_notes(all_rows)}, indent=2), "blood-report-review.json")
        if st.button("Use verified report in chat"):
            from .config import settings
            from .documents import chunk_pages
            from .vectorstore import VectorStore
            source = "Reviewed: " + (upload.name if upload else "Synthetic blood-report example")
            # Use a new source when the verified text changes so older chat cannot mix with it.
            version = hashlib.sha256(json.dumps(originals).encode()).hexdigest()[:12]
            source = f"{source} [{version}]"
            verified_pages = [(item["page"], item["reviewed"]) for item in originals]
            chunks = chunk_pages(verified_pages, source, "lab", settings.chunk_size, settings.chunk_overlap)
            VectorStore("lab").replace_source(chunks)
            st.session_state["source_lab"] = source
            st.success("Verified report selected for chat below.")
