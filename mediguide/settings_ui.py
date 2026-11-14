"""Configuration status and scoped deletion controls."""
import os
import streamlit as st
from .config import settings
from .privacy import user_root
from .vectorstore import VectorStore
from .database import connect


def render_settings() -> None:
    st.header("Settings & privacy")
    connected = settings.llm_provider in {"openai", "openai-compatible"} and bool(settings.llm_api_key)
    st.info("Connected language model configured (availability not verified)." if connected else "Offline evidence mode. Configure LLM_PROVIDER, LLM_BASE_URL, LLM_MODEL and LLM_API_KEY in .env for natural Hindi/English explanations. Restart after changes.")
    st.caption("Never paste API keys into chat or commit .env. Connected mode sends retrieved evidence and recent conversation to your provider.")
    st.info("Authenticated storage is active." if user_root() else "Local demo mode: this computer's demo documents and history are shared. Enable Google sign-in before hosting for others.")
    st.caption("Google setup: ADVANCED_SETUP.md and .streamlit/secrets.toml.example. Authentication currently " + ("required" if os.getenv("MEDIGUIDE_AUTH_REQUIRED", "false").lower() == "true" else "disabled") + ".")
    st.subheader("Remove a document")
    route = st.selectbox("Document collection", ["patient", "lab", "discharge", "insurance"])
    store = VectorStore(route)
    sources = sorted({c.source for c in store.chunks})
    if sources:
        source = st.selectbox("Document to remove", sources)
        confirmed = st.checkbox("Delete this document's index and this collection's saved conversations", key=f"delete_{route}_{source}")
        if st.button("Delete selected document", disabled=not confirmed) and confirmed:
            store.delete_source(source)
            with connect() as conn:
                conn.execute("DELETE FROM documents WHERE filename=? AND route=?", (source, route))
                conn.execute("DELETE FROM conversations WHERE route=? OR route LIKE ?", (route, route + ":%"))
                conn.execute("DELETE FROM feedback WHERE route=?", (route,))
            for key in list(st.session_state):
                if key.startswith(("source_", "claim_", "check_", "ocr_", "schedule_")) or key in {"messages", "policy_checklist", "last_exchange"}:
                    del st.session_state[key]
            st.rerun()
    else:
        st.caption("No documents in this collection.")
    st.caption("Deletion does not remove copies already downloaded, external-provider logs, or backups. This app does not provide encrypted storage or a clinical security certification.")
