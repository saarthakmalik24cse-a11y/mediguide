import json
from pathlib import Path

import numpy as np

from .config import INDEX_DIR, settings
from .embeddings import HashingEmbedder
from .models import Chunk, SearchResult
from .retrieval import lexical_scores, focus_tokens
import re

try:
    import faiss
except ImportError:  # pragma: no cover
    faiss = None


class VectorStore:
    def __init__(self, route: str, directory: Path = INDEX_DIR):
        self.route = route
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.embedder = HashingEmbedder(settings.embedding_dimensions)
        self.chunks: list[Chunk] = []
        self.vectors = np.empty((0, settings.embedding_dimensions), dtype="float32")
        self._load()

    @property
    def metadata_path(self) -> Path:
        return self.directory / f"{self.route}.json"

    @property
    def vectors_path(self) -> Path:
        return self.directory / f"{self.route}.npy"

    def _load(self) -> None:
        if self.metadata_path.exists() and self.vectors_path.exists():
            raw = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            self.chunks = [Chunk(**item) for item in raw]
            self.vectors = np.load(self.vectors_path).astype("float32")

    def _save(self) -> None:
        self.metadata_path.write_text(json.dumps([c.to_dict() for c in self.chunks], indent=2), encoding="utf-8")
        np.save(self.vectors_path, self.vectors)

    def add(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        known = {c.id for c in self.chunks}
        fresh = [c for c in chunks if c.id not in known]
        if not fresh:
            return 0
        vectors = self.embedder.embed([c.text for c in fresh])
        self.chunks.extend(fresh)
        self.vectors = np.vstack([self.vectors, vectors])
        self._save()
        return len(fresh)

    def replace_source(self, chunks: list[Chunk]) -> int:
        """Replace a document version rather than mixing old and new clauses."""
        if not chunks:
            return 0
        sources = {c.source for c in chunks}
        existing = [c for c in self.chunks if c.source in sources]
        if {c.id for c in existing} == {c.id for c in chunks}:
            return 0
        self.chunks = [c for c in self.chunks if c.source not in sources]
        self.vectors = self.embedder.embed([c.text for c in self.chunks])
        return self.add(chunks)

    def search(self, query: str, k: int = 5, source: str | None = None) -> list[SearchResult]:
        if not self.chunks:
            return []
        q = self.embedder.embed([query])
        k = min(k, len(self.chunks))
        candidate_count = len(self.chunks)
        if faiss is not None:
            index = faiss.IndexFlatIP(self.vectors.shape[1])
            index.add(self.vectors)
            scores, indexes = index.search(q, candidate_count)
            pairs = zip(indexes[0], scores[0])
        else:
            all_scores = self.vectors @ q[0]
            indexes = np.argsort(-all_scores)
            pairs = ((i, all_scores[i]) for i in indexes)
        dense = {int(i): float(score) for i, score in pairs if int(i) >= 0}
        lexical, coverage = lexical_scores(query, self.chunks)
        maximum = max(1.0, float(lexical.max()))
        ranked = []
        focus = focus_tokens(query)
        definition = bool(re.match(r"\s*(what is|what are|define|explain)\b", query, re.I))
        for i, chunk in enumerate(self.chunks):
            if source and chunk.source != source:
                continue
            # Reject unrelated candidates instead of filling K with arbitrary text.
            if lexical[i] <= 0 or coverage[i] < 0.25:
                continue
            score = 0.8 * lexical[i] / maximum + 0.2 * max(0, dense.get(i, 0))
            # Public topics have explicit titles. Prefer the requested topic to
            # a subtype or a different medicine that happens to share words.
            title = re.sub(r"^(MedlinePlus|FDA) - ", "", chunk.source)
            exact_topic = focus_tokens(title) == focus
            if chunk.source.startswith(("MedlinePlus - ", "FDA - ")) and exact_topic:
                score += 2
                if definition and chunk.text.lower().startswith(title.lower()):
                    score += 2
                if re.search(r"\b(used|uses|use)\b", query, re.I) and "Indications And Usage:" in chunk.text:
                    score += 2
            ranked.append(SearchResult(chunk, float(score)))
        return sorted(ranked, key=lambda r: r.score, reverse=True)[:k]

    def stats(self) -> dict:
        return {"route": self.route, "chunks": len(self.chunks), "engine": "FAISS" if faiss else "NumPy"}
