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


class CollectionMode(str,Enum):
    CREATE_NEW = "Create_new"
    APPEND_TO_EXISTING ="Append_to_existing"
    REPLACE_EXISTING = "Replace_existing"