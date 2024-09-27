from typing import Any
from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    id: str
    content: str
    document_id: str
    next_chunk_id: str = None
    embedding: list[float] = None


class Entity(BaseModel):
    id: str
    name: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)