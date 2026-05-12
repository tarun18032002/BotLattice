import json
from typing import Any

from src.database.db import Base, SessionLocal, engine
from src.database.models import (
    EmbeddingProviderOption,
    LLMProviderOption,
    VectorDBProviderOption,
)


DEFAULT_OPTIONS: dict[str, Any] = {
    "llm_providers": {
        "anthropic": {
            "label": "Anthropic",
            "models": [
                "claude-sonnet-4-20250514",
                "claude-opus-4-20250514",
                "claude-haiku-4-5-20251001",
            ],
            "requires_api_key": True,
        },
        "openai": {
            "label": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-5.4-mini"],
            "requires_api_key": True,
        },
        "groq": {
            "label": "Groq",
            "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
            "requires_api_key": True,
        },
        "ollama": {
            "label": "Ollama (local)",
            "models": ["llama3.2", "mistral", "phi3", "gemma2"],
            "requires_api_key": False,
        },
        "mistral": {
            "label": "Mistral",
            "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
            "requires_api_key": True,
        },
    },
    "embedding_providers": {
        "huggingface": {
            "label": "HuggingFace",
            "models": ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "BAAI/bge-small-en-v1.5"],
            "requires_api_key": False,
        },
        "google": {
            "label": "Google Gemini",
            "models": ["gemini-embedding-2-preview"],
            "requires_api_key": True,
        },
        "openai": {
            "label": "OpenAI",
            "models": ["text-embedding-3-small", "text-embedding-3-large"],
            "requires_api_key": True,
        },
    },
    "vectordb_providers": {
        "qdrant": {
            "label": "Qdrant",
            "requires_api_key": False,
            "show_api_key": True,
            "url_placeholder": "http://localhost:6333",
            "supports": {
                "distance_metric": True,
                "hybrid_search": True,
                "store_meta": True,
            },
        }
    },
}


SUPPORTED_KEYS = {"llm_providers", "embedding_providers", "vectordb_providers"}


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_option_defaults() -> None:
    _ensure_tables()
    db = SessionLocal()
    try:
        if db.query(LLMProviderOption).count() == 0:
            for provider, meta in DEFAULT_OPTIONS["llm_providers"].items():
                db.add(
                    LLMProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()),
                        models=json.dumps(meta.get("models", [])),
                        requires_api_key=bool(meta.get("requires_api_key", True)),
                    )
                )

        if db.query(EmbeddingProviderOption).count() == 0:
            for provider, meta in DEFAULT_OPTIONS["embedding_providers"].items():
                db.add(
                    EmbeddingProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()),
                        models=json.dumps(meta.get("models", [])),
                        requires_api_key=bool(meta.get("requires_api_key", False)),
                    )
                )

        if db.query(VectorDBProviderOption).count() == 0:
            for provider, meta in DEFAULT_OPTIONS["vectordb_providers"].items():
                supports = meta.get("supports", {}) if isinstance(meta.get("supports"), dict) else {}
                db.add(
                    VectorDBProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()),
                        requires_api_key=bool(meta.get("requires_api_key", False)),
                        show_api_key=bool(meta.get("show_api_key", True)),
                        url_placeholder=meta.get("url_placeholder"),
                        supports_distance_metric=bool(supports.get("distance_metric", True)),
                        supports_hybrid_search=bool(supports.get("hybrid_search", True)),
                        supports_store_meta=bool(supports.get("store_meta", True)),
                    )
                )

        db.commit()
    finally:
        db.close()


def _get_llm_providers(db) -> dict[str, Any]:
    rows = db.query(LLMProviderOption).all()
    return {
        row.provider: {
            "label": row.label,
            "models": json.loads(row.models) if row.models else [],
            "requires_api_key": bool(row.requires_api_key),
        }
        for row in rows
    }


def _get_embedding_providers(db) -> dict[str, Any]:
    rows = db.query(EmbeddingProviderOption).all()
    return {
        row.provider: {
            "label": row.label,
            "models": json.loads(row.models) if row.models else [],
            "requires_api_key": bool(row.requires_api_key),
        }
        for row in rows
    }


def _get_vectordb_providers(db) -> dict[str, Any]:
    rows = db.query(VectorDBProviderOption).all()
    return {
        row.provider: {
            "label": row.label,
            "requires_api_key": bool(row.requires_api_key),
            "show_api_key": bool(row.show_api_key),
            "url_placeholder": row.url_placeholder or "",
            "supports": {
                "distance_metric": bool(row.supports_distance_metric),
                "hybrid_search": bool(row.supports_hybrid_search),
                "store_meta": bool(row.supports_store_meta),
            },
        }
        for row in rows
    }


def get_option(key: str, fallback: Any = None) -> Any:
    if key not in SUPPORTED_KEYS:
        return fallback

    seed_option_defaults()
    db = SessionLocal()
    try:
        if key == "llm_providers":
            return _get_llm_providers(db)
        if key == "embedding_providers":
            return _get_embedding_providers(db)
        if key == "vectordb_providers":
            return _get_vectordb_providers(db)
        return fallback
    except Exception:
        return fallback
    finally:
        db.close()


def set_option(key: str, payload: Any) -> None:
    if key not in SUPPORTED_KEYS or not isinstance(payload, dict):
        return

    _ensure_tables()
    db = SessionLocal()
    try:
        if key == "llm_providers":
            db.query(LLMProviderOption).delete()
            for provider, meta in payload.items():
                db.add(
                    LLMProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()) if isinstance(meta, dict) else provider.title(),
                        models=json.dumps(meta.get("models", []) if isinstance(meta, dict) else []),
                        requires_api_key=bool(meta.get("requires_api_key", True)) if isinstance(meta, dict) else True,
                    )
                )

        elif key == "embedding_providers":
            db.query(EmbeddingProviderOption).delete()
            for provider, meta in payload.items():
                db.add(
                    EmbeddingProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()) if isinstance(meta, dict) else provider.title(),
                        models=json.dumps(meta.get("models", []) if isinstance(meta, dict) else []),
                        requires_api_key=bool(meta.get("requires_api_key", False)) if isinstance(meta, dict) else False,
                    )
                )

        elif key == "vectordb_providers":
            db.query(VectorDBProviderOption).delete()
            for provider, meta in payload.items():
                supports = meta.get("supports", {}) if isinstance(meta, dict) and isinstance(meta.get("supports"), dict) else {}
                db.add(
                    VectorDBProviderOption(
                        provider=provider,
                        label=meta.get("label", provider.title()) if isinstance(meta, dict) else provider.title(),
                        requires_api_key=bool(meta.get("requires_api_key", False)) if isinstance(meta, dict) else False,
                        show_api_key=bool(meta.get("show_api_key", True)) if isinstance(meta, dict) else True,
                        url_placeholder=meta.get("url_placeholder") if isinstance(meta, dict) else None,
                        supports_distance_metric=bool(supports.get("distance_metric", True)),
                        supports_hybrid_search=bool(supports.get("hybrid_search", True)),
                        supports_store_meta=bool(supports.get("store_meta", True)),
                    )
                )

        db.commit()
    finally:
        db.close()


def upsert_provider_option(key: str, provider: str, payload: dict[str, Any]) -> bool:
    if key not in SUPPORTED_KEYS or not provider:
        return False

    _ensure_tables()
    db = SessionLocal()
    try:
        provider = provider.strip().lower()
        if key == "llm_providers":
            row = db.query(LLMProviderOption).filter(LLMProviderOption.provider == provider).first()
            if row is None:
                row = LLMProviderOption(provider=provider, label=provider.title(), models="[]")
                db.add(row)

            row.label = payload.get("label") or row.label
            row.models = json.dumps(payload.get("models", json.loads(row.models or "[]")))
            row.requires_api_key = bool(payload.get("requires_api_key", row.requires_api_key))

        elif key == "embedding_providers":
            row = db.query(EmbeddingProviderOption).filter(EmbeddingProviderOption.provider == provider).first()
            if row is None:
                row = EmbeddingProviderOption(provider=provider, label=provider.title(), models="[]")
                db.add(row)

            row.label = payload.get("label") or row.label
            row.models = json.dumps(payload.get("models", json.loads(row.models or "[]")))
            row.requires_api_key = bool(payload.get("requires_api_key", row.requires_api_key))

        else:
            row = db.query(VectorDBProviderOption).filter(VectorDBProviderOption.provider == provider).first()
            if row is None:
                row = VectorDBProviderOption(provider=provider, label=provider.title())
                db.add(row)

            supports = payload.get("supports", {}) if isinstance(payload.get("supports"), dict) else {}

            row.label = payload.get("label") or row.label
            row.requires_api_key = bool(payload.get("requires_api_key", row.requires_api_key))
            row.show_api_key = bool(payload.get("show_api_key", row.show_api_key))
            row.url_placeholder = payload.get("url_placeholder", row.url_placeholder)
            row.supports_distance_metric = bool(supports.get("distance_metric", row.supports_distance_metric))
            row.supports_hybrid_search = bool(supports.get("hybrid_search", row.supports_hybrid_search))
            row.supports_store_meta = bool(supports.get("store_meta", row.supports_store_meta))

        db.commit()
        return True
    except Exception:
        return False
    finally:
        db.close()


def delete_provider_option(key: str, provider: str) -> bool:
    if key not in SUPPORTED_KEYS or not provider:
        return False

    _ensure_tables()
    db = SessionLocal()
    try:
        provider = provider.strip().lower()

        if key == "llm_providers":
            deleted = db.query(LLMProviderOption).filter(LLMProviderOption.provider == provider).delete()
        elif key == "embedding_providers":
            deleted = db.query(EmbeddingProviderOption).filter(EmbeddingProviderOption.provider == provider).delete()
        else:
            deleted = db.query(VectorDBProviderOption).filter(VectorDBProviderOption.provider == provider).delete()

        db.commit()
        return bool(deleted)
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()
