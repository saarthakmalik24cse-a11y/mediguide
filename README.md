# MediGuide MVP

MediGuide is a local Streamlit RAG MVP with 36 public MedlinePlus health-topic summaries, five selected FDA product labels, synthetic healthcare documents, and a fictional insurance policy. Its core path is:

`PDF → PyMuPDF text extraction → page-aware chunks → local embeddings → FAISS/NumPy index → retrieval → grounded answer → source/page citations`

No API key is required. The default offline answerer extracts relevant source sentences. An OpenAI-compatible chat API can be enabled through environment variables.

> This is an educational prototype, not a medical device, diagnostic system, insurer, or coverage-authority tool. Never upload real patient data to the demo.

## Included modules

- Medical knowledge chat
- Patient PDF upload and chat
- Lab report explainer
- Discharge summary assistant
- Medication information
- A separate insurance-policy RAG route
- Claim preparation checklist
- Page-level source citations and retrieval scores
- Per-route conversational memory
- Local feedback and conversation storage in SQLite
- Admin knowledge-base uploads and document audit view
- Emergency phrase interception, scope limits, disclaimers, and no-context refusal
- Evaluation for Precision@K, Recall@K, Hit Rate, and citation accuracy
- Synthetic sample PDFs and gold-test JSON/CSV templates

## Run locally

Python 3.10–3.12 is recommended.

### Windows PowerShell

```powershell
cd path\to\mediguide
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python seed_data.py
streamlit run app.py
```

### macOS/Linux

```bash
cd path/to/mediguide
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python seed_data.py
streamlit run app.py
```

Open the local URL Streamlit prints (normally `http://localhost:8501`). Run tests with `pytest -q`.

**Windows shortcut:** After setup, double-click `run_mediguide.bat`. Keep its server window open; closing it stops the website. If a browser says the site cannot be reloaded, launch the batch file again. The shortcut uses the bundled virtual environment directly, so PowerShell activation is not needed.

## Optional LLM API

The default `LLM_PROVIDER=extractive` keeps all document processing local. To use an OpenAI-compatible endpoint, edit `.env`:

```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

Only retrieved snippets and recent chat turns are sent to that API. Review the provider's privacy and retention terms before using any sensitive content.

## Structure

```text
mediguide/
├── app.py                    Streamlit interface
├── seed_data.py              Creates and indexes synthetic PDFs
├── mediguide/
│   ├── documents.py          PDF extraction and page-aware chunking
│   ├── embeddings.py         Local deterministic embeddings
│   ├── vectorstore.py        FAISS with NumPy fallback
│   ├── rag.py                Route-scoped retrieval orchestration
│   ├── llm.py                Offline/API LLM abstraction
│   ├── safety.py             Emergency and scope safeguards
│   ├── database.py           SQLite persistence
│   └── evaluation.py         Retrieval/citation metrics
├── data/samples/             Generated synthetic PDFs
├── data/gold/                Gold set and authoring template
└── tests/                    Core pipeline tests
```

## Knowledge routes and isolation

Every chunk carries a `route` and each route has its own index. Medical knowledge, medication labels, patient documents, lab reports, discharge summaries, and insurance policies are not searched together. This keeps retrieval intent clear and reduces accidental cross-domain answers.

Patient documents and the insurance policy are synthetic. The public knowledge snapshot comes from the [MedlinePlus web service](https://medlineplus.gov/about/developers/webservices/) and [openFDA drug-label API](https://open.fda.gov/apis/drug/label/). Each public record retains its original URL, publisher, and retrieval date. MedlinePlus does not endorse this application. FDA examples represent selected product labels, not every formulation or jurisdiction. Insurance answers are limited to the selected policy.

`python seed_data.py` indexes the bundled public snapshot without internet. To refresh the public sources, run `python sync_knowledge.py`. The importer sends only the fixed public topic/drug names in its source code, never uploaded patient documents or conversations. Review sources before using them in a real clinical workflow.

## Evaluation

First run `python seed_data.py`, then use **Admin & evaluation → RAG evaluation**. For each case:

- **Precision@K** = relevant retrieved sources / K retrieved sources.
- **Recall@K** = relevant retrieved sources / all annotated relevant sources.
- **Hit Rate** = 1 when at least one relevant source appears in the top K.
- **Citation accuracy** = valid answer citations pointing to an annotated relevant source / all answer citations. This measures source relevance, not whether every claim is medically correct.
- **Citation validity** separately measures whether citation numbers resolve to retrieved chunks.
- **Abstention correctness** measures refusals on explicitly unanswerable test questions.

Retrieval relevance is annotated at source/page level. Duplicate chunks from a page count once toward retrieval hits. Precision uses the requested K as its denominator even when fewer sources are returned. Public web references use `#p0`; this is a record marker, not an invented PDF page.

Run the broader 18-case development evaluation:

```powershell
python -m mediguide.evaluation data/gold/broader_gold.json --k 3 --output data/gold/broader_results_k3.json
```

CSV input is also supported: separate multiple relevant sources using semicolons. Add `unanswerable=true` for negative cases. The UI runs the broader set. Results from this small, authored development set must not be advertised as real-world medical accuracy.

The retrieval engine combines FAISS cosine similarity with BM25 lexical ranking, common medical aliases, and a minimum lexical-evidence check. Sentence-aware chunks preserve page numbers and short report values. Use **Search within** to select a particular document/policy. Follow-up questions with pronouns incorporate the prior user question. Saved local conversations can be restored from the sidebar.

The supplied cases test the pipeline, not medical correctness. Build a larger gold set with at least two independent clinical/policy reviewers; adjudicate disagreements; stratify by module, document type, difficulty, and unanswerable questions; and freeze a held-out test set. Add groundedness, completeness, refusal quality, latency, and safety-red-team evaluations before any pilot.

## MVP limitations and production hardening

- Hashing embeddings are dependency-light, not state-of-the-art semantic embeddings.
- Extractive mode is intentionally simple; it does not synthesize nuanced answers.
- Image-only scans need OCR.
- Indexes are local and shared by route, not isolated per user/tenant.
- Admin has no authentication in this MVP.
- SQLite stores chats in plain local storage; production requires encryption, access controls, retention/deletion policies, consent, audit logs, and jurisdiction-specific compliance review.
- Add file malware scanning, prompt-injection defenses, approved-domain/source controls, model monitoring, human escalation, and clinician/insurance review.
- Coverage language must always be presented as an aid to locating clauses, never as a coverage determination.
# End-semester submission material

Start with `GUIDELINE_CHECKLIST.md` for the supplied rubric mapping. `PROJECT_REPORT.md` explains the implemented architecture, literature, algorithms and measured results. `VIVA_GUIDE.md` includes frontend/backend explanations, questions and a timed live demo. `PRESENTATION_OUTLINE.md` contains slide-ready content, not a final PPTX. The faculty report template and personal/course details are still required.

In the app, open **More → AI methods lab** to inspect uniform-cost document planning, CSP scheduling and the typed evidence network. These are educational paperwork tools; their costs and day constraints do not establish insurer rules or approval. The functions are kept separately in `mediguide/planning.py` and `mediguide/knowledge_graph.py` for easy explanation.

# Latest health tools (0.8.0-demo)

BMI calculation (chat or calculator), minor-cut first aid, common-illness cards,
and blood-report PDF/OCR review with supplied-range comparisons and conditional
food guidance are now included. See [HEALTH_FEATURES.md](HEALTH_FEATURES.md) for
examples, supported report formatting and important limitations.

## Previous additions (0.7.0-demo)

Question-intent filtering, exact supporting passages, policy-clause progress tracking,
prescription PDF/OCR review, optional Hindi/Hinglish LLM output, Google OIDC gating,
private authenticated document/history storage, and scoped deletion controls are available.
Read [ADVANCED_SETUP.md](ADVANCED_SETUP.md) for configuration and limits.
Google credentials, an LLM API, and OCR language resources are external setup requirements;
none are bundled or claimed to have been clinically validated.

# Run with free local AI on Windows

MediGuide can answer using the bundled sources without an API key. On a fresh checkout, run `setup_mediguide.bat`, then `run_mediguide.bat` and open http://127.0.0.1:8502/.

For optional generated summaries, install and open [Ollama for Windows](https://ollama.com/download/windows), then run `connect_local_ai.bat`. It downloads Qwen3 4B (about 2.5 GB) if needed and saves local settings after the connection test succeeds. Keep Ollama running and restart MediGuide. In chat, enable **Write a fuller answer with local AI** when you want a generated explanation. Local mode uses no paid API.

