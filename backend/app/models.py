from dataclasses import dataclass, field


# This dataclass represents raw source text before it is persisted and chunked.
@dataclass
class SourceDocument:
    id: str
    title: str
    source_label: str
    text: str


# This dataclass represents a retrieval unit produced by the chunker.
@dataclass
class SourceChunk:
    id: str
    document_id: str
    title: str
    source_label: str
    text: str
    start_char: int
    end_char: int
    embedding: list[float] = field(default_factory=list)
