from dataclasses import dataclass, field
from typing import List


# A source document is the top-level unit users ingest into the system.
@dataclass
class Document:
    id: str
    title: str
    source_label: str
    text: str


# A chunk is the unit we actually embed and retrieve against during question answering.
@dataclass
class Chunk:
    id: str
    document_id: str
    title: str
    source_label: str
    text: str
    start_char: int
    end_char: int
    embedding: List[float] = field(default_factory=list)

