import hashlib
import re

import numpy as np


TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]+")


class HashingEmbedder:
    """Deterministic local feature-hashing embeddings; no data leaves the machine."""

    def __init__(self, dimensions: int = 768):
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dimensions), dtype="float32")
        for row, text in enumerate(texts):
            tokens = TOKEN_RE.findall(text.lower())
            for token in tokens:
                raw = hashlib.blake2b(token.encode(), digest_size=8).digest()
                value = int.from_bytes(raw, "little")
                matrix[row, value % self.dimensions] += 1.0 if value & 1 else -1.0
            norm = np.linalg.norm(matrix[row])
            if norm:
                matrix[row] /= norm
        return matrix
