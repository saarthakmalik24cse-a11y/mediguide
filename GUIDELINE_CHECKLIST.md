# End-semester guideline mapping

Rechecked on 14 November 2026 against the three-page `Final Guidelines.docx (1).pdf`. Its substantive rubric matches the earlier guidelines. Release: 0.5.0-demo. Use SUBMISSION_CHECKLIST.md for the remaining submission gates.

| Requirement | Implemented evidence / written deliverable | Status |
|---|---|---|
| Precise problem, real-world relevance, feasible objectives | PROJECT_REPORT.md sections 1–2 | Ready |
| Objectives and flowcharts | Report sections 2–3, Mermaid architecture and workflow | Ready |
| Recent literature and comparative table | Report section 4, primary papers through 2026 | Ready; focused review, not exhaustive |
| State space, initial/goal states, actions, strategy and justification | planning.py: uniform_cost_plan; More > AI methods lab > State-space search; report section 5 | Implemented and tested |
| Knowledge representation, suitability and implementation | knowledge_graph.py; live evidence graph and JSON export; report section 6 | Implemented and tested |
| Intelligent architecture, components, innovation | Report section 3; actual RAG implementation | Ready |
| CSP OR fuzzy logic | planning.py: schedule_tasks; MRV backtracking, domains, dependencies, daily capacity; report section 7 | CSP implemented; fuzzy logic not required because rubric offers an alternative |
| Other AI techniques, if applicable | Hybrid information retrieval, extractive NLP, optional external LLM; report section 8 | Clearly distinguished; no neural training claim |
| AI vs non-AI distinction | Report section 8 | Ready |
| Results, analysis and continuous evaluation | Automated tests, benchmark JSON, report section 9 | Development evidence ready; no historical grading evidence fabricated |
| Ethics, bias and fairness | Report section 10 | Limitations and mitigation documented; no fairness certification |
| Originality | Integrated document explanation and policy preparation with inspectable planning | Rationale documented; bonus marks remain examiner judgment |
| Full report in faculty template | PROJECT_REPORT.md contains report content | Template not supplied; final formatting and student/course details pending |
| Final PPT, viva, demonstration | PRESENTATION_OUTLINE.md and VIVA_GUIDE.md | Slide content ready; PPTX export and rehearsal pending; live viva cannot be completed by code |

The supplied rubric assigns 10 marks to problem formulation + continuous evaluation, 10 to the report, and 20 to final presentation. It allows a reasoned non-applicability explanation for methodology items 2–6, but this implementation includes those topics rather than assuming exemption.

Do not claim: medically validated accuracy, a trained neural embedding model, deployed multi-user security, use of LangChain (the code uses lightweight equivalents), a paid LLM test, or automatic insurer approval.

Before final submission: obtain the faculty report template, add team/roll/course details, verify current source dates, rehearse the working demo and explain algorithm traces. These human/institutional steps cannot be truthfully marked complete in advance.
