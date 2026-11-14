# Health question expansion — 0.8.0-demo

## Where to try it

- **Ask MediGuide:** chat BMI questions or expand Calculate BMI. Examples: `BMI for 55 kg, 160 cm, age 22`; `55 kg, 5 ft 3 in, age 22`; `I cut my finger with scissors, what should I do?`; `What can I do for a common cold?`; `What are common illnesses?`.
- **Lab results → Blood-report scan, range review and diet:** upload a synthetic readable or scanned PDF (5 MB, 10 pages), enable OCR for scans, read, then compare/correct the extracted rows against each original page. Check each verification box to display range comparisons and food information. Try the built-in synthetic example first.

BMI is calculated locally. Adult CDC categories apply from age 20; younger users receive no adult classification. Missing age is requested. Ambiguous heights such as `5,3` are not silently guessed. Pregnancy is not classified. BMI is not a diagnosis or proof of overall health.

First aid and common-cold/headache/diarrhoea cards are short authored summaries with official source links, not live personalised diagnoses. They show basic care and warning signs; they do not prescribe antibiotics, supplements or drug doses. Other topics continue through existing source retrieval. Supported cards do not mean every possible question is covered.

Blood report parsing currently accepts single-line numeric rows such as `Hemoglobin 11.2 g/dL reference 12.0-16.0`. Actual PDF tables may need manual transcription after OCR. Unsupported lines are shown, not silently treated as normal. Values and bounds must share the report's printed units. Missing ranges, inequalities and multiple demographic ranges are not inferred. The app does not diagnose iron deficiency from low hemoglobin, interpret every test, or detect every critical value. Diet notes currently cover iron-related and B12 findings; other abnormalities request clinical interpretation. Report review stays in session memory and exports only on request; the separate document-chat uploader indexes documents as before.

Run `python setup_ocr.py` once for the official English OCR data. Handwriting is not reliable. A clinician must interpret abnormal or critical results in context. Use synthetic data while the application remains a demo.

## References checked 14 November 2026

Validation: 18 new focused tests passed, including BMI units/boundaries, missing
age, ambiguous heights, first aid, rejected lab rows, diet cautions, actual PDF upload and UI flow.
The complete suite passed 93 tests before the additional upload test, which passed separately.
Static mypy checking could not run because mypy is not installed locally.

- https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html
- https://www.nhs.uk/conditions/cuts-and-grazes/
- https://www.nhs.uk/conditions/common-cold/
- https://www.nhs.uk/symptoms/headaches/
- https://www.nhs.uk/symptoms/diarrhoea-and-vomiting/
- https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/
- https://medlineplus.gov/lab-tests/hemoglobin-test/
- https://ods.od.nih.gov/factsheets/Iron-Consumer/
- https://ods.od.nih.gov/factsheets/VitaminB12-Consumer/
