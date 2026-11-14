# Submission and examiner checklist

Reviewed 14 November 2026 against Final Guidelines.docx (1).pdf. This checklist distinguishes implemented evidence from final submission and human assessment.

## Mandatory topic-to-evidence mapping

| Rubric | What to show | What to explain in viva |
|---|---|---|
| Problem statement | PROJECT_REPORT sections 1–2 | Target user, precise input/output, feasibility, scope |
| Literature review | Report section 4 comparative table, references | Why RAG, limitations of existing evaluation, how our integration differs |
| State-space search | More → AI methods lab → State-space search; planning.py | State = collected docs; initial state; required-doc goal; action prerequisites; UCS cost optimality with nonnegative costs |
| Knowledge representation | AI methods lab → Knowledge representation; knowledge_graph.py | Typed semantic network, relations and provenance; mention detection does not infer diagnosis |
| Intelligent design | Report section 3; app.py and rag.py | Frontend, backend, retrieval, storage, answer checks and human verification |
| CSP OR fuzzy logic | AI methods lab → CSP schedule; planning.py | Variables, domains, strict precedence, capacity; MRV backtracking and failure cases. CSP satisfies the alternative |
| Other AI, if applicable | Report section 8 | Retrieval/extraction and optional LLM; no trained neural network or genetic algorithm claimed |
| AI/non-AI distinction | Report section 8 | UCS/CSP/symbolic representation versus UI/PDF parsing/database |
| Human insight theme | Cite a PDF page; change planner costs and constraints | User inspects evidence and interprets outcomes; system does not autonomously prescribe or approve claims |
| Ethics/fairness | Report section 10 | Synthetic data, English/US source bias, demographic limitations, privacy gaps and independent validation needed |
| Results/analysis | Report section 9 and final_review_2026_11_14.json | Precision 38.10%, recall 75%, hit rate 100% on a small authored set; these are not clinical accuracy |

## Final submission gates

- [x] Runnable source, dependency list and environment example.
- [x] Synthetic sample PDFs and local public-reference snapshot.
- [x] State-space search, CSP and semantic network implemented with inspectable traces.
- [x] Report content, comparative literature table and architecture flowchart source.
- [x] 58 automated tests pass; current benchmark saved.
- [x] Viva questions, architecture explanation and timed demo guide.
- [x] Presentation content outline.
- [ ] Actual final PPTX with team details and rehearsal.
- [ ] Official faculty report template received and report formatted to it.
- [ ] Team names, roll numbers, course, section and supervisor details confirmed.
- [ ] Latest release visually checked in the presentation browser and on the presentation laptop.
- [ ] Current local changes synchronized to GitHub and fresh-clone setup checked on a teammate's laptop.
- [ ] Team members can individually explain and run the demo; faculty sign-offs/continuous-assessment evidence supplied by the team if required.

The rubric assigns 10 marks to problem formulation/continuous evaluation, 10 to the report and 20 to presentation (PPT, viva, demo). Originality/ethics bonus is examiner judgment. No marks or clinical certification are guaranteed.

## Examiner-style acceptance cases

Record actual outcome, date and tester during rehearsal; these are manual tasks, not claims of completed verification.

| Action | Expected behaviour |
|---|---|
| Start a fresh checkout with setup_mediguide.bat | Dependencies install, demo indexes build, server starts on 8502 |
| Check release | Sidebar shows 0.5.0-demo |
| Ask a supported health definition | Relevant evidence and source citation; no unrelated disease claim |
| Upload a synthetic selectable-text PDF | Page-aware indexing, selected source, supported values preserved |
| Upload a scanned/empty PDF | Clear unreadable-text/OCR limitation, no invented content |
| Ask for a value absent from the report | Evidence gap rather than a fabricated value |
| Have two different reports/policies | Select one before answering, no cross-record combination |
| Ask an insurance clause/checklist question | Exact selected-policy evidence; no guaranteed approval |
| Change UCS bundle cost from 3 to 8 | Plan changes from bundle to separate collection |
| Make CSP deadline impossible | Explicit infeasible result; no constraint silently removed |
| Reload and download conversation | Screen remains usable and export retains citations |

## What still prevents real production use?

Clinical/policy validation, user authentication and isolation, admin authorization, secure hosting, retention/deletion, upload scanning, monitoring and incident response. Academic rubric coverage does not certify the app for real patient data.
