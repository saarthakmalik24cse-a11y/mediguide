import json
import uuid

import pandas as pd
import streamlit as st

from mediguide.config import DATA_DIR, settings
from mediguide.database import log_document, recent_documents, save_feedback, save_message, saved_sessions, load_session
from mediguide.documents import chunk_pages, extract_pdf
from mediguide.evaluation import evaluate_cases
from mediguide.rag import RAGService
from mediguide.safety import disclaimer
from mediguide.vectorstore import VectorStore

st.set_page_config(page_title="MediGuide • Your care, made clearer", page_icon=":material/spa:", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = {}

ROUTES = {
    "Medical knowledge": ("medical", "Trusted educational reference material"),
    "Patient document chat": ("patient", "Ask questions about an uploaded patient document"),
    "Lab report explainer": ("lab", "Plain-language explanations; never a diagnosis"),
    "Discharge assistant": ("discharge", "Review follow-up and care instructions"),
    "Medication information": ("medication", "Uses, warnings, and label information"),
    "Insurance guidance": ("insurance", "Policy clauses, claims, and checklists"),
}

EXAMPLES = {
    "medical": ["What is diabetes?", "What is high blood pressure?"],
    "patient": ["What follow-up is planned?", "What tests were ordered?"],
    "lab": ["Which hemoglobin value is flagged low?", "What are the platelet and white blood cell values?"],
    "discharge": ["When is the follow-up?", "What warning signs require urgent care?"],
    "medication": ["What is metformin used for?", "What are atorvastatin warnings?"],
    "insurance": ["What are the waiting periods?", "Which documents are required for reimbursement?"],
}
ICONS = ["health_and_safety", "description", "science", "assignment", "medication", "verified_user"]


def navigate(page):
    st.session_state["navigation"] = page


def home():
    st.caption("A LITTLE CLARITY GOES A LONG WAY")
    st.title("Your care, made clearer.")
    st.write("Medical words can feel overwhelming. Let's make sense of your reports, medicines and insurance—one question at a time.")
    st.button("Let's talk about your health", type="primary", icon=":material/arrow_forward:", on_click=navigate, args=("Medical knowledge",))
    st.caption("Source-backed answers · Your documents, explained")
    st.space("large")
    st.subheader("What brings you here?")
    st.caption("Pick one place to start. You can switch whenever you need.")
    titles = ["Understand a health topic", "Read a medical document", "Make sense of lab results", "Plan after-discharge care", "Know your medicine", "Navigate your insurance"]
    descriptions = ["Get a clearer explanation of unfamiliar health terms.", "Find the important details in your PDF.", "Understand the values and notes on your report.", "Find follow-ups and instructions in your summary.", "Look up uses and warnings from label sources.", "Find policy conditions and prepare your claim."]
    entries = list(ROUTES.items())
    for start in (0, 2, 4):
        columns = st.columns(2)
        for offset, col in enumerate(columns):
            title, (_, description) = entries[start + offset]
            with col, st.container(border=True, height=235):
                st.markdown(f":green[:material/{ICONS[start + offset]}:]")
                st.markdown(f"**{titles[start + offset]}**")
                st.caption(descriptions[start + offset])
                st.button("Get started →", key=f"open_{start+offset}", on_click=navigate, args=(title,), width="stretch")


def ingest(upload, route: str) -> tuple[int, int]:
    if upload.size > settings.max_file_mb * 1024 * 1024:
        raise ValueError(f"File exceeds the {settings.max_file_mb} MB limit.")
    data = upload.getvalue()
    if not data.startswith(b"%PDF"):
        raise ValueError("Only valid PDF files are accepted.")
    pages = extract_pdf(data)
    chunks = chunk_pages(pages, upload.name, route, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise ValueError("No readable text was found. Scanned PDFs need OCR, which is not included in this MVP.")
    added = VectorStore(route).replace_source(chunks)
    log_document(upload.name, route, len(pages), added)
    return len(pages), added


def render_upload(route: str, label: str = "Upload a PDF") -> None:
    upload = st.file_uploader(label, type=["pdf"], key=f"upload_{route}",
                              help="Synthetic/demo documents only. Do not upload real patient data to this MVP.")
    if upload and st.button("Read my document", type="primary", key=f"index_{route}"):
        try:
            with st.spinner("Reading your document…"):
                pages, chunks = ingest(upload, route)
            st.session_state[f"source_{route}"] = upload.name
            st.success(f"Your {pages}-page document is ready. Ask a question below.")
        except Exception as exc:
            st.error(str(exc))


def render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    with st.expander(f"Sources used ({len(citations)})"):
        for cite in citations:
            with st.container(border=True):
                location = f"Page {cite['page']}" if cite["page"] else "Public reference"
                st.write(f"[{cite['label']}] {cite['source']} · {location}")
                st.text(cite["excerpt"])
                if cite.get("url"):
                    st.link_button("Open original source", cite["url"])
                    st.caption(f"Retrieved: {cite.get('retrieved_at', 'unknown')}")


def render_chat(route: str, starter: str) -> None:
    st.caption("Answer checks · 11 Nov v2 · Evidence-based demo, not clinically validated")
    if route == "medication":
        st.caption("Drug sources may describe a specific brand or combination product. Check the ingredients and formulation in the original label; do not treat it as a personal prescription.")
    sources = sorted({c.source for c in VectorStore(route).chunks})
    with st.expander("Choose your sources", icon=":material/folder_open:"):
        selected = st.selectbox("Search within", ["All sources"] + sources, key=f"source_{route}")
    source = None if selected == "All sources" else selected
    key = route + ":" + selected
    messages = st.session_state.messages.setdefault(key, [])
    if source:
        with st.expander("Preview selected document"):
            parts = [c for c in VectorStore(route).chunks if c.source == source]
            for part in parts:
                st.caption(f"Page {part.page}" if part.page else "Reference excerpt")
                st.text(part.text)
    if not messages:
        st.space("medium")
        st.subheader("Let's make it clearer.")
        st.caption("What's on your mind? Ask below, or start with one of these.")
    quick_question = None
    for column, example in zip(st.columns(2), EXAMPLES[route]):
        if column.button(example, key=f"quick_{route}_{example}", width="stretch"):
            quick_question = example
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("citations"):
                render_citations(message["citations"])
    question = st.chat_input(starter, key=f"chat_{route}") or quick_question
    if question:
        messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        history = [{"role": m["role"], "content": m["content"]} for m in messages[-7:-1]]
        with st.chat_message("assistant"):
            try:
                with st.spinner("Reviewing the relevant sources…"):
                    result = RAGService(route).ask(question, history, source=source)
            except Exception as exc:
                st.error("The answer could not be generated. Please check the local server window and try again.")
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
                return
            st.markdown(result["answer"])
            if result.get("notice"):
                st.info(result["notice"])
            render_citations(result["citations"])
            st.caption(disclaimer(route))
        messages.append({"role": "assistant", "content": result["answer"], "citations": result["citations"]})
        save_message(st.session_state.session_id, "user", question, [], key)
        save_message(st.session_state.session_id, "assistant", result["answer"], result["citations"], key)
        st.session_state.last_exchange = (question, result["answer"], route)
    if messages:
        transcript = "# MediGuide conversation\n\n" + "\n\n".join(
            f"## {m['role'].title()}\n{m['content']}\n" + "\n".join(
                f"[{c['label']}] {c['source']} — page {c['page']}" + (f" — {c['url']}" if c.get('url') else "")
                for c in m.get('citations', [])) for m in messages)
        st.download_button("Download conversation", transcript, f"mediguide-{route}.md", "text/markdown", key=f"export_{route}")


def claim_checklist() -> None:
    st.subheader("Claim preparation checklist")
    st.button("Plan document collection", icon=":material/event_note:", on_click=navigate, args=("AI methods lab",))
    if st.button("Extract requirements from selected policy"):
        selected = st.session_state.get("source_insurance", "All sources")
        if selected == "All sources":
            st.info("Choose one policy under Search within first.")
        else:
            result = RAGService("insurance").ask("Which claim documents must I submit for reimbursement and what is the deadline?", source=selected)
            st.session_state["policy_checklist"] = (selected, result["answer"], result["citations"])
    saved = st.session_state.get("policy_checklist")
    if saved and saved[0] == st.session_state.get("source_insurance"):
        st.markdown(saved[1])
        render_citations(saved[2])
    st.caption("General preparation reminders")
    claim_type = st.selectbox("Claim route", ["Cashless / pre-authorization", "Reimbursement"])
    items = ["Policy/insurance card", "Government-issued ID", "Treating doctor's advice",
             "Admission or discharge summary", "Prescriptions and diagnostic reports", "Completed claim form"]
    if claim_type.startswith("Cashless"):
        items += ["Network hospital confirmation", "Pre-authorization request/reference number"]
    else:
        items += ["Original itemized hospital bills and receipts", "Cancelled cheque/bank details",
                  "Submission before the policy deadline"]
    for item in items:
        st.checkbox(item, key=f"check_{claim_type}_{item}")
    st.caption("This is a general checklist. Verify every item and deadline against the uploaded policy and insurer instructions.")


with st.sidebar:
    st.header("MediGuide", icon=":material/spa:")
    st.caption("A clearer path through your care")
    st.space("medium")
    page = st.session_state.setdefault("navigation", "Home")
    labels = ["Home", "Ask MediGuide", "My documents", "Lab results", "After discharge", "Medicines", "Insurance"]
    for index, destination in enumerate(["Home"] + list(ROUTES)):
        icon = "home" if index == 0 else ICONS[index-1]
        st.button(labels[index], key=f"nav_{destination}", icon=f":material/{icon}:", type="primary" if page == destination else "tertiary", width="stretch", on_click=navigate, args=(destination,))
    st.space("medium")
    with st.expander("Saved conversations"):
        st.caption("Local demo history on this computer")
        saved = st.selectbox("Conversation", ["Choose a conversation"] + saved_sessions())
        if st.button("Restore conversation") and saved != "Choose a conversation":
            st.session_state.session_id = saved
            st.session_state.messages = load_session(saved)
            st.rerun()
        if st.button("Start new conversation"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = {}
            st.rerun()
    with st.expander("More"):
        for destination in ("Feedback", "AI methods lab", "Admin & evaluation"):
            st.button(destination, key=f"nav_{destination}", on_click=navigate, args=(destination,), width="stretch")
        st.caption("Offline source excerpts" if settings.llm_provider == "extractive" or not settings.llm_api_key else "Connected language model")
        st.caption("Educational demo with synthetic patient documents. Clinical decisions belong to your clinician; policy decisions belong to your insurer.")

st.caption("YOUR CARE SPACE  /  " + ("WELCOME" if page == "Home" else page.upper()))

if page == "Home":
    home()
elif page in ROUTES:
    route, description = ROUTES[page]
    st.header(page)
    st.caption(description)
    if route in {"patient", "lab", "discharge", "insurance"}:
        with st.expander("Add a document", icon=":material/upload_file:"):
            render_upload(route, "Choose a synthetic/demo PDF")
            examples = {"patient": "synthetic_patient_document.pdf", "lab": "synthetic_lab_report.pdf",
                        "discharge": "synthetic_discharge_summary.pdf", "insurance": "synthetic_insurance_policy.pdf"}
            sample_path = DATA_DIR / "samples" / examples[route]
            if sample_path.exists():
                st.download_button("Try an example PDF", sample_path.read_bytes(), sample_path.name, "application/pdf")
    elif route in {"medical", "medication"}:
        with st.expander("Browse the reference library", icon=":material/menu_book:"):
            library = {c.source: c.metadata for c in VectorStore(route).chunks}
            st.write(f"{len(library)} sources available")
            for name, metadata in library.items():
                if metadata.get("url"):
                    st.link_button(name, metadata["url"])
                else:
                    st.write(name + " (demo or uploaded document)")
    if route == "insurance":
        chat_col, check_col = st.tabs(["Talk about your policy", "Prepare a claim"])
        with chat_col:
            render_chat(route, "Ask about coverage, exclusions, waiting periods, or claims")
        with check_col:
            claim_checklist()
    else:
        prompts = {
            "medical": "Ask a general health question",
            "patient": "Ask a question about the uploaded document",
            "lab": "Ask what a lab value or note means",
            "discharge": "Ask about instructions, warning signs, or follow-up",
            "medication": "Ask about uses, warnings, or adverse effects",
        }
        render_chat(route, prompts[route])

elif page == "Feedback":
    st.header("Feedback")
    if "last_exchange" not in st.session_state:
        st.info("Ask a question in any module first, then return here to rate the latest answer.")
    else:
        question, answer, route = st.session_state.last_exchange
        st.write(f"**Latest question:** {question}")
        rating = st.radio("Was the answer useful and grounded?", [1, 0], format_func=lambda x: "👍 Yes" if x else "👎 No", horizontal=True)
        note = st.text_area("Optional note (do not include personal health information)")
        if st.button("Submit feedback", type="primary"):
            save_feedback(question, answer, rating, note, route)
            st.success("Feedback saved locally.")

elif page == "AI methods lab":
    from mediguide.coursework_ui import render_coursework
    render_coursework()
else:
    st.header("Admin & evaluation")
    admin_tab, eval_tab, audit_tab = st.tabs(["Knowledge upload", "RAG evaluation", "Audit"])
    with admin_tab:
        admin_route = st.selectbox("Knowledge route", ["medical", "medication", "insurance"])
        render_upload(admin_route, "Upload a trusted-source PDF")
        st.warning("MVP note: production deployments must add authentication, authorization, malware scanning, and source approval workflows.")
    with eval_tab:
        st.write("Citation accuracy checks annotated source relevance, not clinical correctness. Use the broader gold set from the command line for additional topics and unanswerable questions.")
        k = st.slider("K", 1, 10, 5)
        if st.button("Run evaluation", type="primary"):
            path = DATA_DIR / "gold" / "broader_gold.json"
            with st.spinner("Evaluating…"):
                rows, summary = evaluate_cases(path, k)
            st.session_state.evaluation = (rows, summary)
        if "evaluation" in st.session_state:
            rows, summary = st.session_state.evaluation
            st.caption(f"Last run: {summary['cases']} cases, K={summary['k']}. Development benchmark; not clinical validation.")
            cols = st.columns(4)
            for col, metric in zip(cols, ["precision_at_k", "recall_at_k", "hit_rate", "citation_accuracy"]):
                col.metric(metric.replace("_", " ").title(), f"{summary[metric]:.1%}")
            st.dataframe(pd.DataFrame(rows), width="stretch")
            st.download_button("Download results", json.dumps({"summary": summary, "cases": rows}, indent=2), "evaluation-results.json")
    with audit_tab:
        docs = recent_documents()
        st.dataframe(pd.DataFrame(docs), width="stretch") if docs else st.info("No documents indexed yet.")
