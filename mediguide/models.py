from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    page: int
    route: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchResult:
    chunk: Chunk
    score: float
