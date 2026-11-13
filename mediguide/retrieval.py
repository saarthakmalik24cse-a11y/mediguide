"""Local BM25 signals and conservative query normalization."""
import re
from collections import Counter
import numpy as np

STOP = set("a an the is are was were what which how why when where does do did of to for and or in on with my me i it its this that please explain tell about should can could would from as at be have has report document policy according mean means describe give written says say".split())
STOP.update("much many information details people person elderly older adults old require required need needs know want related regarding also all some".split())
INTENT_WORDS = set("used use uses symptoms symptom treatment treatments warning warnings cautions precautions documents submit submission dose dosage dosing daily".split())


def focus_tokens(text):
    terms = set(tokens(text))
    return terms - INTENT_WORDS or terms
ALIASES = {"hba1c": "a1c glucose", "hypertension": "blood pressure", "anaemia": "anemia",
           "haemoglobin": "hemoglobin", "paracetamol": "acetaminophen", "copay": "co pay",
           "followup": "follow up", "reimbursement": "reimbursement claim", "cbc": "blood count"}


def tokens(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    expanded = " ".join(ALIASES.get(w, w) for w in words)
    return [w for w in expanded.split() if w not in STOP and len(w) > 1]


def lexical_scores(query, chunks):
    query_terms = set(tokens(query))
    corpus = [Counter(tokens(c.text + " " + c.metadata.get("title", ""))) for c in chunks]
    lengths = np.array([sum(c.values()) for c in corpus], dtype=float)
    avg = max(1.0, float(lengths.mean()))
    scores = np.zeros(len(chunks), dtype=float)
    coverage = np.zeros(len(chunks), dtype=float)
    for term in query_terms:
        freq = np.array([c[term] for c in corpus], dtype=float)
        df = np.count_nonzero(freq)
        idf = np.log(1 + (len(chunks) - df + 0.5) / (df + 0.5))
        scores += idf * freq * 2.5 / (freq + 1.5 * (0.25 + 0.75 * lengths / avg))
        coverage += freq > 0
    return scores, coverage / max(1, len(query_terms))
