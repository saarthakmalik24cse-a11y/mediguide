"""A typed semantic network grounded in actual stored chunks.

Relations express provenance and literal mentions, not clinical causation.
"""
import re

CONCEPTS = {
    "diabetes": ["diabetes"], "hypertension": ["hypertension", "high blood pressure"],
    "hemoglobin": ["hemoglobin", "haemoglobin"], "iron": ["iron"],
    "waiting period": ["waiting period"], "claim": ["claim", "reimbursement"],
    "follow-up": ["follow-up", "follow up"],
}


def build_graph(chunks):
    nodes, edges = {}, set()
    for chunk in chunks:
        route_id = "route:" + chunk.route
        doc_id = "doc:" + chunk.route + ":" + chunk.source
        chunk_id = "chunk:" + chunk.id
        nodes[route_id] = {"id": route_id, "type": "Route", "label": chunk.route}
        nodes[doc_id] = {"id": doc_id, "type": "Document", "label": chunk.source}
        nodes[chunk_id] = {"id": chunk_id, "type": "Evidence", "label": f"{chunk.source} / page {chunk.page}",
                           "page": chunk.page, "url": chunk.metadata.get("url")}
        edges.add((route_id, "contains", doc_id))
        edges.add((doc_id, "has_evidence", chunk_id))
        for concept, aliases in CONCEPTS.items():
            if any(re.search(r"\b" + re.escape(alias) + r"\b", chunk.text, re.I) for alias in aliases):
                concept_id = "concept:" + concept
                nodes[concept_id] = {"id": concept_id, "type": "Concept", "label": concept}
                edges.add((chunk_id, "mentions", concept_id))
    return {"nodes": sorted(nodes.values(), key=lambda n: n["id"]),
            "edges": [{"subject": a, "relation": b, "object": c} for a, b, c in sorted(edges)]}
