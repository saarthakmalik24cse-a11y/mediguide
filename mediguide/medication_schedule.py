"""Conservative transcription of labelled instructions, never a prescribing engine."""
import re
from collections import Counter

FIELDS = ("medicine", "dose", "frequency", "timing", "food", "duration")
LABEL = re.compile(r"(?:^|[|;\n])\s*(Medicine|Dose|Frequency|Timing|Food|Duration)\s*:\s*", re.I)
DEMO = "Medicine: Demo medicine A | Dose: 1 tablet | Frequency: once daily | Timing: morning | Food: after breakfast | Duration: 3 days\nMedicine: Demo medicine B | Dose: not specified | Frequency: BD"


def build_draft(pages: list[tuple[str, int, str]]) -> dict:
    rows = []
    for source, page, text in pages:
        # Each medicine starts a new block; preserve all source text separately.
        starts = list(re.finditer(r"(?im)^\s*Medicine\s*:", text))
        for index, start in enumerate(starts):
            evidence = text[start.start():starts[index + 1].start() if index + 1 < len(starts) else len(text)].strip()
            matches = list(LABEL.finditer(evidence))
            fields = {}
            issues = []
            for i, match in enumerate(matches):
                key = match.group(1).lower()
                value = evidence[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(evidence)].strip()
                if key in fields:
                    issues.append(f"Repeated {key} label: confirm original instructions")
                    fields[key] += " / " + value
                else:
                    fields[key] = value
            for key in FIELDS:
                if not fields.get(key):
                    fields[key] = "Not stated — confirm"
                    issues.append(f"Missing {key}")
            if re.search(r"\b(?:OD|BD|BID|TID|QID|PRN|SOS|HS)\b|\d\s*-\s*\d\s*-\s*\d", evidence):
                issues.append("Shorthand present: ask a pharmacist to interpret it")
            rows.append(dict(fields, source=source, page=page, evidence=evidence,
                             status="Unverified transcription — confirm current prescription", issues=issues))
    counts = Counter(row["medicine"].casefold().strip() for row in rows)
    for row in rows:
        if counts[row["medicine"].casefold().strip()] > 1:
            row["issues"].append("Repeated medicine name: kept separate; confirm whether duplicate or changed")
    return {"status": "DRAFT ONLY — not a treatment plan; may be incomplete",
            "instructions": rows,
            "source_pages": [{"source": s, "page": p, "text": t} for s, p, t in pages]}
