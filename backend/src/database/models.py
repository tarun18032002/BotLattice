from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Text, DateTime
from sqlalchemy.types import Enum

from src.database.db import Base
from src.pipeline.config.enums import ChunkingType



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class ChunkingRequest(Base):
    __tablename__ = "chunking_requests"

    id = Column(Integer, ForeignKey("auth_users.id"), primary_key=True, index=True)
    chunking_type = Column(
        Enum(ChunkingType, name="chunking_type_enum"),
        nullable=False
    )
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=50)
    language = Column(String, default="python")
    chunk_lines = Column(Integer, default=40)
    chunk_lines_overlap = Column(Integer, default=10)
    chunk_sizes = Column(String, default="[2048, 512, 128]")


class CollectionState(Base):
    __tablename__ = "collection_state"

    id = Column(Integer, ForeignKey("auth_users.id"), primary_key=True, index=True)
    mode = Column(String, default="Append_to_existing")
    collection_name = Column(String, default="documents")
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)


class EmbeddingState(Base):
    __tablename__ = "embedding_state"

    id = Column(Integer, primary_key=True, default=1)
    provider = Column(String, default="")
    model = Column(String, default="")
    api_key = Column(String, nullable=True)
    batch_size = Column(Integer, default=512)
    normalize = Column(Boolean, default=False)
    cache = Column(Boolean, default=False)
    connected = Column(Boolean, default=False)
    dimension = Column(Integer, default=0)


class VectorDBState(Base):
    __tablename__ = "vectordb_state"

    id = Column(Integer, primary_key=True, default=1)
    vectordb_type = Column(String, default="qdrant")
    url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    distance_metric = Column(String, default="Cosine")
    hybrid_search = Column(Boolean, default=False)
    store_meta = Column(Boolean, default=True)
    connected = Column(Boolean, default=False)


class LLMSettingsState(Base):
    __tablename__ = "llm_settings_state"

    id = Column(Integer, primary_key=True, default=1)
    llmProvider = Column(String, default="anthropic")
    llmModel = Column(String, default="claude-sonnet-4-20250514")
    apiKey = Column(String, nullable=True)
    temperature = Column(Float, default=0.2)
    maxTokens = Column(Integer, default=1024)
    defaultTopK = Column(Integer, default=5)
    simThreshold = Column(Float, default=0.75)
    reranking = Column(Boolean, default=False)
    multiQuery = Column(Boolean, default=True)
    compression = Column(Boolean, default=False)
    showSources = Column(Boolean, default=True)
    streamResponses = Column(Boolean, default=False)
    systemPrompt = Column(Text, nullable=False)


class LLMProviderOption(Base):
    __tablename__ = "llm_provider_options"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, unique=True, index=True, nullable=False)
    label = Column(String, nullable=False)
    models = Column(Text, nullable=False)
    requires_api_key = Column(Boolean, default=True)


class EmbeddingProviderOption(Base):
    __tablename__ = "embedding_provider_options"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, unique=True, index=True, nullable=False)
    label = Column(String, nullable=False)
    models = Column(Text, nullable=False)
    requires_api_key = Column(Boolean, default=False)


class VectorDBProviderOption(Base):
    __tablename__ = "vectordb_provider_options"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, unique=True, index=True, nullable=False)
    label = Column(String, nullable=False)
    requires_api_key = Column(Boolean, default=False)
    show_api_key = Column(Boolean, default=True)
    url_placeholder = Column(String, nullable=True)
    supports_distance_metric = Column(Boolean, default=True)
    supports_hybrid_search = Column(Boolean, default=True)
    supports_store_meta = Column(Boolean, default=True)


class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    auth_provider = Column(String, nullable=False, default="password")
    google_sub = Column(String, unique=True, nullable=True)


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)