"""Download public educational sources only; never sends uploaded documents."""
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

import requests

from mediguide.config import DATA_DIR
from mediguide.documents import chunk_pages
from mediguide.vectorstore import VectorStore

TOPICS = ["diabetes", "high blood pressure", "cholesterol", "anemia", "asthma",
          "kidney diseases", "thyroid diseases", "dehydration", "pneumonia",
          "heart diseases", "arthritis", "allergy", "blood tests", "nutrition",
          "mental health", "digestive diseases", "sleep disorders", "infections"]
DRUGS = ["amoxicillin", "metformin", "ibuprofen", "acetaminophen", "atorvastatin"]
SNAPSHOT = DATA_DIR / "knowledge" / "public_sources.json"


def plain(text):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(text))).strip()


def index_records(records):
    counts = {}
    for route in ("medical", "medication"):
        store = VectorStore(route)
        chunks = []
        for record in records:
            if record["route"] != route:
                continue
            parts = chunk_pages([(0, record["text"])], record["source"], route)
            for part in parts:
                part.metadata.update({k: record[k] for k in ("url", "publisher", "retrieved_at", "title")})
                part.metadata["kind"] = "public_reference"
            chunks.extend(parts)
        # Replace only this importer’s records, retaining all user PDFs.
        store.chunks = [c for c in store.chunks if c.metadata.get("kind") != "public_reference"]
        store.vectors = store.embedder.embed([c.text for c in store.chunks])
        counts[route] = store.add(chunks)
    return counts


def main():
    records = {}
    if SNAPSHOT.exists():
        records = {r["url"]: r for r in json.loads(SNAPSHOT.read_text(encoding="utf-8"))}
        age = time.time() - SNAPSHOT.stat().st_mtime
        if age < 12 * 3600:
            print("Using public-source cache (less than 12 hours old).", index_records(list(records.values())))
            return
    session = requests.Session()
    session.headers["User-Agent"] = "MediGuide-Educational-MVP/0.2"
    timestamp = datetime.now(timezone.utc).isoformat()
    failures = []
    for topic in TOPICS:
        try:
            response = session.get("https://wsearch.nlm.nih.gov/ws/query", params={
                "db": "healthTopics", "term": topic, "retmax": 2, "tool": "MediGuide"}, timeout=30)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for doc in root.findall(".//document"):
                fields = {n.get("name", "").lower(): plain("".join(n.itertext())) for n in doc.findall("content")}
                summary = fields.get("fullsummary", "")
                if not summary:
                    continue
                url = doc.get("url")
                title = fields.get("title", topic)
                records[url] = dict(route="medical", source="MedlinePlus - " + title,
                                    title=title, text=title + "\n" + summary, url=url,
                                    publisher="MedlinePlus / National Library of Medicine", retrieved_at=timestamp)
            print("MedlinePlus:", topic, flush=True)
        except (requests.RequestException, ET.ParseError) as exc:
            failures.append(f"{topic}: {exc}")
        time.sleep(0.8)
    for drug in DRUGS:
        try:
            response = session.get("https://api.fda.gov/drug/label.json", params={
                "search": f'openfda.generic_name:"{drug}"', "limit": 1}, timeout=30)
            response.raise_for_status()
            record = response.json()["results"][0]
            url = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=" + record["set_id"]
            sections = []
            for field in ("indications_and_usage", "purpose", "warnings", "warnings_and_cautions", "contraindications", "adverse_reactions"):
                if record.get(field):
                    sections.append(field.replace("_", " ").title() + ": " + plain(" ".join(record[field])))
            if not sections:
                continue
            title = drug.title() + " — selected product label"
            records[url] = dict(route="medication", source="FDA - " + drug.title(), title=title,
                                text=title + "\n" + "\n".join(sections), url=url,
                                publisher="openFDA drug labeling", retrieved_at=timestamp)
            print("FDA:", drug, flush=True)
        except (requests.RequestException, KeyError, IndexError) as exc:
            failures.append(f"{drug}: {exc}")
        time.sleep(0.8)
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(list(records.values()), indent=2, ensure_ascii=False), encoding="utf-8")
    print("Indexed:", index_records(list(records.values())))
    print("Public source records:", len(records))
    if failures:
        print("Refresh failures (previous records retained):", "\n".join(failures))


if __name__ == "__main__":
    main()
