"""Local-only prescription review screen."""
import json
import pymupdf
import streamlit as st
from .medication_schedule import build_draft, DEMO, FIELDS


def clear_draft() -> None:
    st.session_state.pop("schedule_draft", None)


def render_schedule() -> None:
    st.header("Your medicine instructions", icon=":material/schedule:")
    st.caption("Bring the written instructions together. Review every detail before using them.")
    st.warning("Demo only. This draft does not determine which prescriptions are current, check interactions, or recommend doses. Confirm the combined plan with your pharmacist.")
    with st.expander("Supported format and limits"):
        st.write("Use synthetic, text-based PDFs with labelled Medicine, Dose, Frequency, Timing, Food and Duration fields. Ordinary unlabelled prescriptions, handwriting and scanned images are not automatically understood. Missing details stay missing; twice daily is not converted to clock times. Compare every page for omitted medicines.")
        st.code(DEMO, language=None)
    uploads = st.file_uploader("Add prescription PDFs (up to 5, 5 MB each)", type=["pdf"], accept_multiple_files=True, key="schedule_files", on_change=clear_draft)
    if st.button("Prepare review draft", key="schedule_build", type="primary", disabled=not uploads):
        clear_draft()
        try:
            if not uploads or len(uploads) > 5:
                raise ValueError("Choose between 1 and 5 PDFs.")
            pages = []
            for number, upload in enumerate(uploads, 1):
                data = upload.getvalue()
                if len(data) > 5 * 1024 * 1024 or not data.startswith(b"%PDF"):
                    raise ValueError("Each file must be a PDF smaller than 5 MB.")
                with pymupdf.open(stream=data, filetype="pdf") as doc:
                    if doc.needs_pass or len(doc) > 20:
                        raise ValueError("Use unlocked PDFs with at most 20 pages each.")
                    for i, page in enumerate(doc, 1):
                        text = page.get_text().strip()
                        if not text:
                            raise ValueError(f"File {number}, page {i} has no readable text. OCR is not supported; no combined draft was created.")
                        pages.append((f"{number}. {upload.name}", i, text))
            st.session_state.schedule_draft = build_draft(pages)
        except Exception as exc:
            st.error(f"Could not prepare the draft: {exc}")
    if st.button("Try synthetic example", key="schedule_demo"):
        st.session_state.schedule_draft = build_draft([("Synthetic example (not your uploads)", 1, DEMO)])
    draft = st.session_state.get("schedule_draft")
    if not draft:
        return
    st.subheader("Review draft · not a confirmed schedule")
    st.caption("Kept in this session only; not indexed, saved to the database, or sent to an LLM API.")
    if not draft["instructions"]:
        st.info("No supported labelled medicine blocks found. Read the original text below; this does not mean no medicines were prescribed.")
    for row in draft["instructions"]:
        with st.container(border=True):
            st.text(row["medicine"])
            st.caption(f"{row['source']} · page {row['page']} · Unverified")
            for field in FIELDS[1:]:
                st.text(f"{field.title()}: {row[field]}")
            for issue in row["issues"]:
                st.warning(issue)
            with st.expander("Original instruction"):
                st.text(row["evidence"])
    with st.expander("Check ALL original pages for omissions"):
        for page in draft["source_pages"]:
            st.caption(f"{page['source']} · page {page['page']}")
            st.text(page["text"])
    st.download_button("Download review draft (JSON)", json.dumps(draft, indent=2, ensure_ascii=False), "medicine-review-draft.json", mime="application/json")
    st.button("Clear draft", on_click=clear_draft)
