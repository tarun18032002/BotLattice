from enum import Enum


class ChunkingType(str, Enum):
    sentence = "sentence"
    token = "token"
    code = "code"
    html = "html"
    markdown = "markdown"
    hierarchical = "hierarchical"
    simple = "simple"


class EmbeddingProvider(str, Enum):
    openai = "openai"
    huggingface = "huggingface"
    ollama = "ollama"


class VectorDBType(str, Enum):
    QDRANT = "qdrant"
    chroma = "chroma"
    pinecone = "pinecone"