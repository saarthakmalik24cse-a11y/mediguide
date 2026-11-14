# MediGuide 0.7 setup and honest capability boundaries

## Answers first

Offline mode selects cited source sentences; it is not a general language model and cannot answer every medical question. This release checks question intent before selecting a sentence (dose, warning, cause, timing, symptom or treatment). It shows verbatim supporting passages where available. No source match means clarification rather than an unrelated answer. These checks do not prove clinical correctness or semantic entailment.

For natural English/Hindi/Hinglish answers, configure the existing `.env` template with `LLM_PROVIDER=openai-compatible`, your provider's base URL, model and API key, then restart. Never commit credentials. API errors or failed citation/number checks fall back to original source excerpts, which may be English. Common Hindi/Hinglish query phrases are normalized locally; arbitrary multilingual retrieval remains limited. Language generation cannot supply missing knowledge. Expand the approved source library and independently review it before expecting broad topic coverage.

## Google login and private data

Install requirements (now includes `streamlit[auth]`). Register a Google OIDC web application. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, fill its client credentials and a strong random cookie secret. Configure the exact callback `http://localhost:8502/oauth2callback` in Google for the local demo. Set `MEDIGUIDE_AUTH_REQUIRED=true` in `.env` and restart. For hosting, configure the actual HTTPS callback at both ends.

Authenticated users receive separate document indexes and SQLite histories under `data/users/<hash-of-issuer-and-subject>/`. Public medical/medication references are shared. Existing local-demo uploads are not migrated into accounts. Administration defaults to denied; `MEDIGUIDE_ADMIN_SUBJECTS` is a comma-separated allowlist of verified Google subject IDs (not emails or names). Local mode is explicitly shared and must not be publicly exposed. Google sign-in cannot be end-to-end verified without your OAuth credentials.

Settings & privacy can delete a selected private document index, collection history, upload audit entries and feedback. Downloaded exports, backups and provider-held logs are outside this deletion. Encryption, malware scanning, backup policy, session revocation and independent security review are still deployment work.

## Prescription OCR with human review

Open Prescription review. Select a synthetic PDF and Read pages. For scans enable OCR. Compare each original page with extracted text and manually enter labelled medicine instructions; confirm every page before creating a schedule draft. Editing text resets its confirmation. Original OCR text is retained in the draft export alongside the user transcription. No dose, time or active prescription is inferred.

Run `python setup_ocr.py` once to download official Tesseract English model data and its license into `data/ocr` (network required). OCR uses PyMuPDF's Tesseract interface and automatically detects this folder; alternatively configure a system tessdata path (`TESSDATA_PREFIX`). See https://pymupdf.readthedocs.io/en/latest/installation.html and https://github.com/tesseract-ocr/tessdata_fast . Missing OCR resources produce an actionable error, not an empty schedule. Handwriting remains unreliable. Native text PDF review works without OCR resources. Limits: 5 MB, 10 pages. This is not a validated prescription reader.

## Claim tracker and evaluation

Select one policy in Insurance, then Prepare a claim. Explicit document-requirement clauses become separate checkboxes, with page references and optional/conditional markers. A clause may contain multiple documents: check the whole clause. Progress is self-reported and extraction may omit clauses; it is not an approval or completeness guarantee. General reminders remain separate.

Run `python -m pytest -q` and `python -m mediguide.evaluation data/gold/broader_gold.json --k 3`. Automated tests and lexical answer checks are development evidence, not expert validation. `data/gold/reviewer_template.json` records independent clinician/insurance reviewer assessments; no review is pre-filled as passed. Keep a held-out set and report unsupported questions separately.
