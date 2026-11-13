import hashlib
import re
from pathlib import Path

import pymupdf

from .models import Chunk


def extract_pdf(data: bytes) -> list[tuple[int, str]]:
    doc = pymupdf.open(stream=data, filetype="pdf")
    pages = []
    for number, page in enumerate(doc, start=1):
        text = re.sub(r"[ \t]+", " ", page.get_text("text"))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        pages.append((number, text))
    doc.close()
    return pages


def chunk_pages(pages: list[tuple[int, str]], filename: str, route: str,
                chunk_size: int = 900, overlap: int = 150) -> list[Chunk]:
    chunks: list[Chunk] = []
    if chunk_size < 100 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Chunk size must be at least 100 and overlap smaller than the chunk size.")
    for page, text in pages:
        if not text:
            continue
        # Keep complete sentences/lines together and preserve short report values.
        units = re.split(r"(?<=[.!?])\s+|\n+", text)
        pieces, current = [], ""
        for unit in units:
            if not unit.strip():
                continue
            if current and len(current) + len(unit) + 1 > chunk_size:
                pieces.append(current)
                previous = re.split(r"(?<=[.!?])\s+|\n+", current)[-1]
                current = previous if len(previous) <= overlap else ""
            current = (current + "\n" + unit).strip()
        if current:
            pieces.append(current)
        for index, piece in enumerate(pieces):
            digest = hashlib.sha1(f"{route}|{filename}|{page}|{index}|{piece}".encode()).hexdigest()[:16]
            chunks.append(Chunk(digest, piece, Path(filename).name, page, route,
                                {"chunk_index": index}))
    return chunks
