from pydantic import BaseModel, Field
from typing import Optional, List
from .enums import ChunkingType,EmbeddingProvider,VectorDBType,CollectionMode


# -----------------------------
# Chunking Config
# -----------------------------

class ChunkingRequest(BaseModel):

    chunking_type: ChunkingType

    chunk_size: Optional[int] = 512
    chunk_overlap: Optional[int] = 50

    # Code splitter params
    language: Optional[str] = "python"
    chunk_lines: Optional[int] = 40
    chunk_lines_overlap: Optional[int] = 10

    # Hierarchical params
    chunk_sizes: Optional[List[int]] = Field(
        default_factory=lambda: [2048, 512, 128]
    )


# -----------------------------
# Embedding Config
# -----------------------------

class EmbeddingRequest(BaseModel):

    provider: EmbeddingProvider = EmbeddingProvider.openai

    model_name: str = "text-embedding-3-small"

    batch_size: Optional[int] = 32


# -----------------------------
# Vector DB Config
# -----------------------------

class VectorDBRequest(BaseModel):

    vectordb_type: VectorDBType = VectorDBType.QDRANT

    # collection_name: str = "documents"

    url: Optional[str] = None
    api_key: Optional[str] = None

# -----------------------------
# Collection Request
# -----------------------------

class CollectionRequest(BaseModel):
    mode: CollectionMode = CollectionMode.APPEND_TO_EXISTING
    collection_name: str = "documents"
    description: Optional[str] = None
    tags: Optional[str] = None # Or List[str] if you split the string later


# -----------------------------
# Ingestion Request
# -----------------------------

class IngestRequest(BaseModel):

    chunking: ChunkingRequest

    embedding: EmbeddingRequest

    vectordb: VectorDBRequest


