# MediGuide 0.5.0-demo

## Implemented

- Compact responsive home cards without fixed heights; native theme and controls.
- A visible document selector and clear source scope on every chat route.
- Direct extractive answers first; supporting details in an expander. Full answer/citations remain in downloads and history.
- Evidence/clarification status without misleading confidence percentages.
- A persistent release identifier to distinguish different running copies.
- A Demo readiness page with six-module index checks, rehearsal sequence and deployment limitations.
- Launcher preflight via `check_setup.py`.
- Conversation-storage failure no longer prevents viewing/downloading an answer.
- Empty/overlong question handling and existing cross-document safeguards.

## Verify on your laptop

Run `setup_mediguide.bat` on a fresh checkout with Python 3.12 installed. Run `python -m pytest -q` and `python check_setup.py` in the environment. Start `run_mediguide.bat`; the browser should display `0.5.0-demo`. Close an older server yourself if it occupies port 8502; the launcher does not terminate unknown processes.

Open More → Demo readiness, then rehearse document chat, insurance checklist, citations, unsupported questions and AI methods. The current changes were checked with headless UI tests; desktop/mobile visual inspection remains a separate check.

## Production gate — NOT complete

This is a local single-user educational demo. Missing production controls include authenticated tenant isolation, admin authorization, privacy/retention/deletion policies, secure deployment, upload scanning, rate limiting, monitoring, and independent clinical/policy review. OCR and robust multilingual understanding are not implemented. Offline responses remain extractive; optional API generation is not clinically validated. No real patient deployment or universal accuracy claim is supported.

GitHub hosts the code, not the running website. Public deployment requires a separately agreed hosting/privacy design. Do not expose the current shared local storage to real patients.
