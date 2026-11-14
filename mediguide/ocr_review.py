"""PDF text/OCR staged for human correction before downstream use."""
import pymupdf
from .config import DATA_DIR


def read_review_pages(data: bytes, use_ocr: bool = False) -> list[dict]:
    if len(data) > 5 * 1024 * 1024 or not data.startswith(b"%PDF"):
        raise ValueError("Choose a PDF smaller than 5 MB.")
    rows = []
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        if doc.needs_pass or not 1 <= len(doc) <= 10:
            raise ValueError("Use an unlocked PDF with 1–10 pages.")
        for i, page in enumerate(doc, 1):
            text = page.get_text()
            if use_ocr:
                try:
                    local_data = DATA_DIR / "ocr"
                    tp = page.get_textpage_ocr(language="eng", dpi=150, full=True,
                                              tessdata=str(local_data) if (local_data / "eng.traineddata").exists() else None)
                    text = page.get_text(textpage=tp)
                except Exception as exc:
                    raise ValueError("OCR engine/language data unavailable. Configure Tesseract English data (see ADVANCED_SETUP.md).") from exc
            scale = min(1.0, 1200 / max(page.rect.width, page.rect.height, 1))
            rows.append({"page": i, "original": text, "image": page.get_pixmap(matrix=pymupdf.Matrix(scale, scale)).tobytes("png")})
    return rows


def render_ocr_review() -> None:
    import hashlib
    import streamlit as st
    from .medication_schedule import build_draft
    st.header("Read and review a prescription")
    st.warning("Synthetic documents only. OCR can misread medicine names, decimals and units. Handwriting is not reliably supported. Compare every entry with the original before continuing.")
    upload = st.file_uploader("Prescription PDF · up to 10 pages / 5 MB", type=["pdf"], key="ocr_upload")
    if upload is None:
        st.session_state.pop("ocr_pages", None)
        return
    data = upload.getvalue()
    fingerprint = hashlib.sha256(data).hexdigest()
    if st.session_state.get("ocr_fingerprint") != fingerprint:
        st.session_state.pop("ocr_pages", None)
        st.session_state.ocr_fingerprint = fingerprint
    use_ocr = st.checkbox("Use OCR for scanned pages", key="ocr_engine")
    if st.button("Read pages", type="primary"):
        st.session_state.pop("ocr_pages", None)
        try:
            with st.spinner("Reading pages for review…"):
                st.session_state.ocr_pages = read_review_pages(data, use_ocr)
                st.session_state.ocr_run = st.session_state.get("ocr_run", 0) + 1
        except ValueError as exc:
            st.error(str(exc))
    pages = st.session_state.get("ocr_pages", [])
    reviewed = []
    confirmed = []
    for page in pages:
        key = f"{fingerprint}_{st.session_state.ocr_run}_{page['page']}"
        left, right = st.columns(2)
        with left:
            st.image(page["image"], caption=f"Original · page {page['page']}", alt="Original prescription page for transcription comparison")
        with right:
            st.text_area("Extracted text (reference)", page["original"], disabled=True, key="raw_" + key)
            st.caption("Transcribe each medicine as Medicine: … | Dose: … | Frequency: … | Timing: … | Food: … | Duration: … . Leave unstated details blank. Keep stop/change instructions verbatim.")
            corrected = st.text_area("Reviewed labelled instructions", key="corrected_" + key, height=180)
            verified_hash = hashlib.sha256(corrected.encode()).hexdigest()
            confirmed.append(st.checkbox("I compared this transcription with the original page", key="verified_" + key + verified_hash))
            reviewed.append((upload.name + " (user-reviewed transcription)", page["page"], corrected))
    if pages and st.button("Create schedule review draft", disabled=not all(confirmed)):
        if not all(confirmed) or not any(text.strip() for _, _, text in reviewed):
            st.error("Review and transcribe the instructions first.")
            return
        draft = build_draft(reviewed)
        draft["original_extraction"] = [{"source": upload.name, "page": p["page"], "text": p["original"]} for p in pages]
        st.session_state.schedule_draft = draft
        st.session_state.navigation = "Medicine schedule"
        st.rerun()
