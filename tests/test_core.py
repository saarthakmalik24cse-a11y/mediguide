from pathlib import Path

import pymupdf

from mediguide.documents import chunk_pages, extract_pdf
from mediguide.embeddings import HashingEmbedder
from mediguide.safety import emergency_message
from mediguide.vectorstore import VectorStore


def pdf_bytes(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_chunk_and_retrieve(tmp_path: Path):
    pages = extract_pdf(pdf_bytes("Policy waiting period is twenty four months for demo conditions."))
    chunks = chunk_pages(pages, "demo.pdf", "insurance", chunk_size=200, overlap=20)
    store = VectorStore("insurance_test", tmp_path)
    store.add(chunks)
    results = store.search("waiting period months", 1)
    assert results and results[0].chunk.source == "demo.pdf"
    assert results[0].chunk.page == 1


def test_embeddings_are_normalized():
    vector = HashingEmbedder(128).embed(["blood glucose glucose"])[0]
    assert 0.99 < float((vector @ vector)) < 1.01


def test_emergency_guard():
    assert emergency_message("I have severe chest pain")
    assert emergency_message("What is HbA1c?") is None
