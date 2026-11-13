# MediGuide — start here

## On this computer

Double-click **run_mediguide.bat**, then open http://localhost:8501. Keep the server window open.

## On a new Windows computer

Install Python 3.12, extract the complete project folder, and double-click **setup_mediguide.bat**. First setup needs internet to install Python packages. Later launches use **run_mediguide.bat**.

## Try the app

1. Open **Home** and select any tool.
2. For patient, lab, discharge, or insurance tools, download the synthetic example or upload your own synthetic PDF.
3. Click **Index document**, then select its name under **Search within**.
4. Click a suggested question or type your own. Expand the answer's sources to inspect the evidence.
5. For insurance, choose a single policy and click **Extract requirements from selected policy**.
6. Download your conversation, rate an answer under **Feedback**, or restore a saved local conversation from the sidebar.
7. Open **Admin & evaluation** to add reference PDFs or run the development benchmark.

The default answerer quotes relevant source sentences and needs no API key. For generated explanations, configure the optional API in `.env` following README.md. Scanned PDFs without selectable text require OCR before upload. This is a single-computer educational MVP; public multi-user hosting and clinician validation are not included.

## Simple code map

- `app.py`: screens, buttons, uploads, and chat.
- `mediguide/documents.py`: PDF text extraction and chunks.
- `mediguide/vectorstore.py` and `retrieval.py`: source search.
- `mediguide/rag.py` and `llm.py`: evidence and answers.
- `mediguide/database.py`: history and feedback.
- `mediguide/evaluation.py`: retrieval and citation checks.

Your public-reference snapshot is dated September 2026. Refresh with `python sync_knowledge.py` when internet is available. Source dates are visible in citations.
