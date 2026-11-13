# Answer-quality update — 11 November 2026

## Fixes

- Normalize a small explicit set of wording variants, including oldage and dosage typos. This is not general language understanding.
- Distinguish older-adult dietary iron requirements from personalized treatment doses, using the NIH reference checked on 11 November.
- Remove generic demographic/question words from retrieval focus so unrelated sentences do not qualify merely because they mention older people.
- Prioritize exact public-reference topic titles and indication sections for drug-use questions.
- Require sentence-level topic overlap rather than matching only generic intent words such as used or dose.
- Report abstention when no cited answer could be assembled, even if some chunks were retrieved.
- Add a visible answer-check version marker and a medication-specific formulation warning.

## Testing

`tests/test_answer_quality.py` includes wording variations, missing evidence, exact values/units, source isolation, wrong-drug rejection and regression checks against the local corpus. Controlled fixtures cover medical knowledge, patient documents, labs, discharge, medication and insurance. `tests/test_app.py` exercises the exact screenshot question through the chat widget.

Reproduce with `python -m pytest -q` from the project folder.

The existing 18-case authored retrieval benchmark was rerun at K=3. Results are in `data/gold/accuracy_v4_results.json`:

| Metric | Result |
|---|---:|
| Precision@3 | 38.10% |
| Recall@3 | 75.00% |
| Hit rate | 100% |
| Citation-source relevance | 100% |
| Citation label validity | 100% |
| Correct abstention on 4 annotated negative cases | 100% |

Compared with the previous recorded run, precision and recall decreased while source-citation relevance increased. Exact-topic preference retrieves more chunks from the same relevant page, so the distinct-page evaluator rewards fewer unique hits. This is a trade-off, not an across-the-board accuracy improvement. The same authored cases were used during development; these are regression results, not independent validation.

## Remaining limitations

The offline system still selects excerpts; it cannot reliably synthesize every request, interpret arbitrary Hinglish, or guarantee a direct answer to any medical question. Some FDA snapshots describe combination products, which must not be presented as single-ingredient prescribing guidance. The UI warns about this and preserves the original product text. Corpus selection needs further expert review.

No clinical correctness percentage is claimed. Source relevance and valid labels do not establish entailment or safety. Before real-patient use, obtain independent clinician review, policy-expert review, held-out answer-level tests and production privacy controls. Do not use fabricated patient data as medical evidence. Optional API mode has not been validated in these offline tests.

## See the new version

Refresh the app and ask the question again. Previously saved answers are historical and are not rewritten. The chat should show `Answer checks · 11 Nov v2`. If absent, close your existing MediGuide server terminal and reopen `run_mediguide.bat` from this project. The local health endpoint responded successfully during verification; health alone does not establish which code revision the running process imported.
