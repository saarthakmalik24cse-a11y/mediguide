"""Generate synthetic demo PDFs and index them. Safe to run repeatedly."""
from pathlib import Path

import pymupdf

from mediguide.config import DATA_DIR, settings
from mediguide.database import log_document
from mediguide.documents import chunk_pages, extract_pdf
from mediguide.vectorstore import VectorStore

SAMPLES = {
    "medical_knowledge_demo.pdf": ("medical", [
        "HbA1c educational overview\nHbA1c is a blood test that estimates average blood glucose over roughly the previous two to three months. It is commonly used to monitor diabetes. Interpretation depends on clinical context, laboratory methods, and clinician guidance.",
        "Creatinine educational overview\nCreatinine is a waste product measured in blood. Clinicians use it with age and other factors to estimate kidney filtration. A result outside a reference range does not by itself establish a diagnosis.",
    ]),
    "medication_label_demo.pdf": ("medication", [
        "Demo medication label: Amoxicillin\nAmoxicillin is a penicillin-class antibacterial medicine used for certain susceptible bacterial infections. It does not treat viral infections. Important warnings include serious hypersensitivity reactions. Patients should seek urgent help for trouble breathing, facial swelling, or severe rash.",
        "Adverse reactions and use\nCommonly reported adverse reactions include nausea, vomiting, diarrhea, and rash. Dosing must be determined by a qualified prescriber based on the infection, patient factors, and kidney function. This synthetic summary is for software demonstration only.",
    ]),
    "synthetic_lab_report.pdf": ("lab", [
        "SYNTHETIC DEMO — NOT A REAL PATIENT\nComplete Blood Count\nHemoglobin: 11.2 g/dL (demo reference 12.0–15.5) — flagged low. White blood cells: 7.1 x10^9/L (demo reference 4.0–11.0). Platelets: 245 x10^9/L (demo reference 150–400). Results must be interpreted by a clinician with symptoms and history.",
    ]),
    "synthetic_discharge_summary.pdf": ("discharge", [
        "SYNTHETIC DEMO DISCHARGE SUMMARY\nReason for stay: uncomplicated dehydration after gastroenteritis. Follow-up: contact primary clinician within 3 days. Instructions: take fluids as advised and resume diet gradually. Seek urgent care for fainting, confusion, inability to keep fluids down, blood in vomit or stool, or worsening symptoms.",
    ]),
    "synthetic_patient_document.pdf": ("patient", [
        "SYNTHETIC DEMO — NOT A REAL PATIENT\nVisit note: adult patient reports fatigue. Clinician plan: review sleep, diet, current medicines, and ordered CBC and thyroid testing. No diagnosis is established in this note. Follow-up is planned after results are available.",
    ]),
    "synthetic_insurance_policy.pdf": ("insurance", [
        "SYNTHETIC DEMO HEALTH POLICY\nCoverage: eligible inpatient hospitalization expenses are covered subject to policy limits and exclusions. Cashless service requires treatment at a network hospital and prior authorization except where the emergency process applies. Approval is not guaranteed until the insurer reviews the request.",
        "Waiting periods and exclusions\nA 30-day initial waiting period applies except to covered accidental injury. Listed pre-existing conditions have a 24-month waiting period. Cosmetic procedures without medical necessity and experimental treatment are excluded in this fictional policy.",
        "Reimbursement claim documents\nSubmit the completed claim form, discharge summary, original itemized bills and receipts, prescriptions, diagnostic reports, identity proof, and bank details within 30 days after discharge. Keep copies. This fictional deadline is for demo use only.",
    ]),
}


def create_pdf(path: Path, pages: list[str]) -> None:
    if path.exists():
        path.unlink()
    doc = pymupdf.open()
    for text in pages:
        text = text.translate(str.maketrans({"—": "-", "–": "-", "−": "-"}))
        page = doc.new_page()
        page.insert_textbox(pymupdf.Rect(60, 60, 535, 780), text, fontsize=12, lineheight=1.5)
    doc.save(path)
    doc.close()


def main() -> None:
    sample_dir = DATA_DIR / "samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    for filename, (route, pages) in SAMPLES.items():
        path = sample_dir / filename
        create_pdf(path, pages)
        extracted = extract_pdf(path.read_bytes())
        chunks = chunk_pages(extracted, filename, route, settings.chunk_size, settings.chunk_overlap)
        added = VectorStore(route).replace_source(chunks)
        log_document(filename, route, len(pages), added)
        print(f"{filename}: {added} new chunks")
    from sync_knowledge import SNAPSHOT, index_records
    import json
    if SNAPSHOT.exists():
        print("Public knowledge:", index_records(json.loads(SNAPSHOT.read_text(encoding="utf-8"))))


if __name__ == "__main__":
    main()
