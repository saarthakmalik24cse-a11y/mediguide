# 0.7 development validation

The automated suite passed 76 tests on 14 November 2026, including 13 new intent,
evidence, policy scope, native PDF review, identity isolation and auth-gate checks.
The running Streamlit agent interface also rendered the new navigation and answer-language control.
An English OCR sample was processed locally using official tessdata_fast resources;
spacing changed, demonstrating why human correction is mandatory.

The existing 18-case development retrieval benchmark at K=3 remains:
Precision 0.38095; Recall 0.75; Hit rate 1.0; annotated source citation relevance 1.0;
citation label validity 1.0; negative-case abstention 1.0.
See data/gold/release07_results.json. These are not clinical correctness rates.

Google OAuth sign-in needs the user's client credentials for an end-to-end test.
The Authlib/mypy package installation did not complete in this session; the
stalled installers were stopped. Re-run `python -m pip install -r requirements.txt`
before activating authentication. Static type checking remains pending.
Natural multilingual generation needs an LLM provider and key. Neither is claimed
to have been verified against a live provider. Independent expert review is pending;
data/gold/reviewer_template.json is an unreviewed template, not evaluation evidence.
