# Medicine schedule review (0.6.0-demo)

Open **Medicine schedule** in the sidebar. Try the synthetic example or upload up to five text-based synthetic PDF prescriptions, then choose **Prepare review draft**.

This is a conservative transcription helper, not a fully automatic prescription reader. Supported blocks start with `Medicine:` on a new line and use explicit `Dose:`, `Frequency:`, `Timing:`, `Food:` and `Duration:` labels separated by newlines, pipes or semicolons. Example:

    Medicine: Demo medicine A | Dose: 1 tablet | Frequency: once daily | Timing: morning | Food: after breakfast | Duration: 3 days

Every entry retains its filename, page and original text. Missing fields remain unfilled, shorthand is flagged, and repeated names remain separate. All source pages are available to check omissions. JSON downloads retain the draft warning and evidence. The screen does not store uploads in the knowledge index or database or call an LLM. Clear draft removes the extracted draft; remove uploaded files separately in the uploader.

Limitations: no OCR, unlabelled free-text parsing, medicine reconciliation, interaction checks, reminders or confirmation of current prescriptions. The parser does not detect every conflict or ambiguity. A pharmacist must review the combined plan; it must not be used as treatment instructions. Max 5 MB and 20 pages per file. Any unreadable page rejects the entire combined draft.

## Suggested next priorities

1. Evidence highlighting and answerability checks across all modules, with a larger independently reviewed benchmark.
2. OCR with side-by-side human correction before extracting any medicine instructions.
3. Policy-specific claim completeness tracker, separating required documents from optional ones and showing each clause.
4. Plain-language Hindi/English explanations with the original medical terms and units preserved.
5. Authenticated patient isolation, deletion controls, and access-controlled administration before hosting for others.

These are proposed future improvements, not implemented features or clinical validation.
