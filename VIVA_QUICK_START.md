# MediGuide: understand and demonstrate the implementation

## Thirty-second explanation

MediGuide is a Python application that helps users find and understand information in medical references and synthetic patient/insurance PDFs. It retrieves relevant evidence and shows source/page citations. It does not train a medical model or replace a clinician or insurer. Its default answer mode selects source sentences; an optional external LLM can generate explanations using those sentences as context.

## What we used

| Layer | Technology | Responsibility |
|---|---|---|
| Main language | Python | Application and algorithm code |
| Frontend | Streamlit | Navigation, upload, chat, source previews, feedback |
| Backend | Python modules | Parsing, retrieval, answering, safety and evaluation |
| PDF parsing | PyMuPDF | Extract selectable text with page numbers; no OCR |
| Embedding | Deterministic feature hashing + NumPy | Text-to-vector conversion; not a trained transformer |
| Search | FAISS with NumPy fallback + BM25 | Similarity and keyword ranking |
| Persistent storage | SQLite | Conversations, feedback and document audit metadata |
| Index storage | JSON + NumPy files | Chunk text, metadata and vectors |
| Optional generation | OpenAI-compatible HTTP API | External model via an abstraction; not required offline |
| Testing | pytest + Streamlit AppTest | Algorithm, evidence and UI regressions |

The frontend and backend are in one Streamlit Python process. We did not build React, FastAPI or a separately trained neural network. LangChain is not used: the RAG stages are explicit small Python functions.

## Explain a question from start to finish

1. Choose a module and document. Different records or policies must not be mixed.
2. Upload a synthetic PDF. Extract page text, split into chunks, retain source/page metadata.
3. Convert chunks into vectors and save the index locally.
4. Normalize the question and run route/source-filtered hybrid retrieval.
5. Select relevant sentences offline, or pass context to the configured model.
6. Check generated citation labels and whether numbers occur in cited evidence. These checks do not prove medical correctness.
7. Show the answer and sources; persist conversation and feedback.

## What makes a good answer?

A direct response to the question, only supported details, precise numbers/units/conditions, clear citations and an explicit evidence gap when the answer is absent. Useful next steps must be supported or framed as clarification, not an invented treatment plan or coverage promise.

Tests are not the same as clinical accuracy. Report retrieval metrics separately from answer correctness. Use independent clinician/policy review and a held-out question set before claiming real-world safety. The current small authored benchmark is a development regression set.

## Run on a group member's Windows laptop

Install Python 3.12, download/clone the repository, then double-click `setup_mediguide.bat`. It creates the environment, installs requirements, builds demo indexes and starts the app. Later use `run_mediguide.bat`. Keep the server terminal open and visit http://127.0.0.1:8502/.

Terminal alternative:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed_data.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Localhost is not a public hosted website. Each laptop starts its own server. A GitHub repository shares code, not the running app. Public hosting requires a separate deployment and privacy/security review; do not upload real patient records to this prototype.

For rubric algorithms, literature, complexity and viva questions see `PROJECT_REPORT.md` and `VIVA_GUIDE.md`. The official faculty report template and final PPTX are still pending.
