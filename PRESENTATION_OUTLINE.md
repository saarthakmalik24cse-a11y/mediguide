# MediGuide final presentation content

Slide-ready content draft; not an exported PPTX. Add your real team/course details. Suggested duration: 8 minutes plus demo and questions.

## 1 — MediGuide

Evidence-grounded healthcare document assistance and insurance preparation.
Human understanding first: explain, cite, inspect—not diagnose or approve.

## 2 — Problem and objectives

Medical reports and policies are technical and fragmented. Generic chat can lack document evidence.
Objectives: page-aware PDF chat, separate knowledge routes, citations, explainable planning and measurable evaluation.

## 3 — Literature and project position

Compare Lewis et al. RAG (2020), MedRAG/MIRAGE (2024), MedRGB (2024 preprint) and MRAG (2026 preprint).
Use the comparative table and references in PROJECT_REPORT.md section 4. Do not compare our small benchmark numerically with their larger studies.

## 4 — Architecture

User → Streamlit → PDF extraction → chunks → hashing vectors/index → hybrid retrieval → evidence gate → extractive/API answer → citations.
SQLite stores conversations/feedback. Separate route/source filters constrain retrieval.

## 5 — State-space search

State = collected documents; goal = all required documents. Actions have prerequisites and effort costs.
UCS uses a min-heap and best-cost pruning. Example: identity present → bundle (3) → form (1): total 4.
Explain why BFS does not minimize unequal costs.

## 6 — Knowledge representation

Route contains Document; Document has Evidence; Evidence mentions Concept.
Show an actual exported edge and its page/source provenance. Dictionary mentions are not medical inference.

## 7 — CSP

Task variables, day domains, strict precedence, availability, deadline and daily capacity.
Backtracking + MRV + forward checking. Show a feasible schedule and an infeasible deadline.
This satisfies the CSP alternative; fuzzy logic is not implemented.

## 8 — AI versus conventional software

AI: search, constraint reasoning, symbolic representation; NLP retrieval/extraction and optional LLM.
Non-AI: Streamlit widgets, PDF parsing, SQLite and downloads.
No local neural training; no claim that FAISS is an LLM.

## 9 — Results and analysis

Use the current test count and measured results in PROJECT_REPORT.md section 9 and guidelines_results_k3.json.
18 authored cases; K=3. Explain low precision alongside high hit rate.
Citation-source relevance is not medical correctness. The benchmark is small and not independently clinically reviewed.

## 10 — Ethics, limitations and future work

Synthetic documents only; clinician/insurer remains decision-maker.
Limitations: no OCR, lexical/hash retrieval, local shared storage, source freshness and language bias.
Next: independently reviewed evaluations, semantic embeddings and authenticated isolation.

## 11 — Live demonstration

PDF question → cited page → unsupported question → policy checklist → UCS → CSP → evidence graph.
Follow VIVA_GUIDE.md; verify the server before presenting.

## 12 — References and questions

Include the exact primary-source references from PROJECT_REPORT.md.
Invite questions about state, action, constraints, provenance and evaluation definitions.
