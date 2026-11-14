"""Policy-backed candidate requirements; no inferred approval or completeness."""
import hashlib
import re


def policy_items(chunks, source: str) -> list[dict]:
    items, seen = [], set()
    for chunk in chunks:
        if chunk.source != source:
            continue
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", chunk.text):
            sentence = sentence.strip()
            if not re.search(r"\b(submit|required|must|provide|attach|optional|may include)\b", sentence, re.I):
                continue
            if not re.search(r"\b(documents?|bills?|receipts?|reports?|forms?|summary|identity|prescription|certificate|proof)\b", sentence, re.I):
                continue
            key = (chunk.page, sentence)
            if key in seen:
                continue
            seen.add(key)
            items.append({"id": hashlib.sha256(f"{source}|{chunk.page}|{sentence}".encode()).hexdigest()[:20],
                          "clause": sentence, "page": chunk.page, "source": source,
                          "kind": "Optional / conditional — review" if re.search(r"\b(optional|may|if|unless)\b", sentence, re.I) else "Requirement candidate — review"})
    return items


def render_tracker(source: str) -> None:
    import streamlit as st
    from .vectorstore import VectorStore
    items = policy_items(VectorStore("insurance").chunks, source)
    st.subheader("Your policy document tracker")
    st.caption("Each checkbox covers the complete quoted clause, which may list several documents. Mark it only after checking every item. Progress is self-reported, not insurer approval.")
    if not items:
        st.info("No explicit document-requirement clauses found. Check the full policy or ask your insurer; this is not a complete checklist.")
        return
    ready = 0
    missing = []
    for item in items:
        st.caption(f"{item['kind']} · {source} · page {item['page']}")
        st.text(item["clause"])
        checked = st.checkbox("I have checked all items in this clause", key="claim_" + item["id"])
        ready += int(checked)
        if not checked:
            missing.append(item["clause"])
    st.progress(ready / len(items), text=f"{ready}/{len(items)} candidate clauses checked")
    st.download_button("Download remaining clauses", "Unverified policy checklist\n\n" + "\n\n".join(missing), "remaining-claim-clauses.txt")
