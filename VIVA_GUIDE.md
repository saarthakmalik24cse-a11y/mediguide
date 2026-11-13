# MediGuide viva guide

## Your 45-second introduction

MediGuide helps people understand medical documents and insurance paperwork using retrieved evidence rather than unsupported answers. Users select a module, upload a synthetic PDF and ask a question. The system extracts page-aware text, retrieves relevant chunks and displays an explanation with citations. Our project also demonstrates uniform-cost search for document collection, a CSP solver for scheduling, and a semantic network for evidence provenance. It supports human understanding; it does not diagnose, prescribe or approve insurance claims.

## Frontend and backend: explain in this order

1. **Frontend — `app.py`:** Streamlit renders navigation, upload, chat, sources and feedback. There is no separate React frontend. Clicking a widget reruns the script; session state retains UI context.
2. **Extraction:** PyMuPDF reads selectable PDF text page by page. Scanned images require OCR, which is not implemented.
3. **Chunking:** text is divided into manageable evidence units while preserving filename, route and page. Smaller evidence units make retrieval more focused.
4. **Embedding/indexing:** deterministic hashing converts text features into vectors. Normalized vectors support similarity ranking. These are not trained neural embeddings. FAISS accelerates search; a NumPy fallback is supported.
5. **Retrieval:** vector ranking and BM25 lexical ranking find relevant evidence. Route and source filters keep policy queries separate from medical collections. Weak matches are refused.
6. **Answering:** default offline mode extracts relevant sentences. Optional API mode asks an external LLM to explain retrieved context. Retrieval improves grounding but does not guarantee truth.
7. **Citations:** source IDs resolve to evidence and page metadata. A valid reference is not proof that every sentence is medically correct.
8. **Persistence:** SQLite stores conversations and feedback; local index files store chunks and vectors. This is a single-user demo, not an authenticated hospital system.

## Mandatory AI demonstrations

Open **More → AI methods lab**.

### Uniform-cost search

- State: documents already collected. Initial state: user selection. Goal: required documents are present.
- Action: obtain a document/bundle when prerequisites hold. Cost: nonnegative demo effort units.
- Algorithm: expand the least-total-cost state using a min-heap; prune inferior paths to the same state.
- Demo: identity already available; bundle effort 3 gives total effort 4. Change bundle effort to 8 and recompute: separate collection gives 5.
- Why not BFS? BFS minimizes number of steps, not unequal effort costs.
- Why not A*? We do not need to invent a heuristic for this small domain.
- Optimality applies to the supplied model only, not real insurer processing time.

### CSP

- Variables: four preparation tasks. Domains: allowed day numbers.
- Constraints: prerequisites strictly earlier, daily capacity, availability and deadline.
- Strategy: backtracking, minimum remaining values (MRV), and forward checking.
- Demo: default settings produce a feasible schedule. Set deadline to day 1 and recompute to demonstrate infeasibility.
- It finds a feasible schedule, not the shortest or cheapest schedule. No fuzzy logic is claimed; the rubric allows CSP OR fuzzy logic.

### Knowledge representation

- Typed semantic network: Route → Document → Evidence → Concept.
- Relations: contains, has_evidence, mentions.
- Show the edges and download JSON. Explain how an evidence node retains page/source provenance.
- A dictionary-detected mention is not a diagnosis or causal relationship. The graph is an inspection feature, not the current retrieval algorithm.

## Questions the examiner may ask

| Question | Accurate short answer |
|---|---|
| Why RAG? | It lets answers use inspectable document evidence and update the corpus without retraining a model. |
| Where is the AI? | UCS, CSP and symbolic knowledge representation; retrieval/extractive NLP support answers, with optional generative AI. |
| Is PDF extraction AI? | No. Extraction, UI, SQLite and file export are conventional software components. |
| Did you train an LLM? | No. Offline mode is extractive; optional generation calls a configured external model. |
| Is FAISS the chatbot? | No. It is a similarity-search library. |
| Did you use LangChain? | No. We implemented lightweight orchestration explicitly for readability. |
| Why separate routes? | To avoid retrieving a fictional policy as general medical evidence, and to support selected-document questions. |
| How does insurance work? | Upload/select a policy, retrieve relevant clauses, inspect cited checklist requirements, then use the demonstration planner. Coverage and approval remain insurer decisions. |
| How does memory work? | UI state and persisted conversation history retain messages; limited previous-question context helps follow-ups. It is not model retraining. |
| What if the answer is absent? | Reject weak evidence or say what is missing instead of inventing a fact. Refusal rules are imperfect. |
| What does Precision@K mean? | Relevant retrieved items divided by K, using the evaluator's distinct source/page definition. |
| Recall@K? | Relevant retrieved items divided by all annotated relevant items. |
| Hit rate? | Fraction of answerable questions retrieving at least one relevant item. |
| Citation accuracy? | Our automated metric checks relevance of cited source/pages, not full clinical entailment. |
| Is 100% hit rate 100% medical accuracy? | No. This small authored benchmark is not clinical validation or an independent test population. |
| What are the limitations? | Lexical/hash retrieval, no OCR, small evaluation set, limited languages, shared local storage and imperfect safety rules. |
| Is this optimal code? | Small separated functions and explicit algorithms make it explainable. UCS optimizes modeled cost; CSP is exponential in the worst case. No universal performance claim. |
| What is original? | The integrated evidence explanation and inspectable paperwork planning workflow, not a newly invented algorithm. |

## Six-minute live demo

1. **0:00–0:45:** state the problem and scope; show Home.
2. **0:45–2:00:** select a synthetic patient PDF, ask a supported question, open its citation and page. Ask an unrelated question to demonstrate limitations.
3. **2:00–3:00:** choose Insurance, select synthetic policy, ask about required documents and extract its checklist. Explain fictional policy limitations.
4. **3:00–4:00:** open AI methods lab; run UCS, change bundle effort, explain the changed plan.
5. **4:00–4:45:** show feasible and infeasible CSP settings; inspect semantic-network edges.
6. **4:45–5:30:** show evaluation results and explain precision versus hit rate.
7. **5:30–6:00:** state ethics, limitations and next steps. Keep a screenshot backup, but distinguish it from a live run.

## Before submission

- Read `PROJECT_REPORT.md` and map each requirement using `GUIDELINE_CHECKLIST.md`.
- Obtain the official report template; add real team, roll number, faculty and course details. Do not invent approvals or signatures.
- Use `PRESENTATION_OUTLINE.md` to prepare the required PPT; an outline is not a final PowerPoint file.
- Rehearse the above demo locally, with API mode off unless you have tested your own configured endpoint.
- Run tests and evaluation again; report measured results, including weaknesses.
- Never upload real patient data for the viva.
