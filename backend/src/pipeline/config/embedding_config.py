"""Active embedding configuration persisted in PostgreSQL."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional

from src.database.db import Base, SessionLocal, engine
from src.database.models import EmbeddingState as EmbeddingStateModel

_LEGACY_CONFIG_FILE = Path(__file__).parent / "embedding_state.json"


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _load_legacy_json() -> "EmbeddingConfig | None":
    if not _LEGACY_CONFIG_FILE.exists():
        return None

    try:
        data = json.loads(_LEGACY_CONFIG_FILE.read_text(encoding="utf-8"))
        allowed = {k: v for k, v in data.items() if k in EmbeddingConfig.__dataclass_fields__}
        return EmbeddingConfig(**allowed)
    except Exception:
        return None


@dataclass
class EmbeddingConfig:
    provider: str = ""
    model: str = ""
    api_key: Optional[str] = None
    batch_size: int = 512
    normalize: bool = False
    cache: bool = False
    connected: bool = False
    dimension: int = 0  # Extracted from actual embedding model

    def save(self, user_id: int = 1) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(EmbeddingStateModel).filter(EmbeddingStateModel.id == user_id).first()
            if row is None:
                row = EmbeddingStateModel(id=user_id)
                db.add(row)

            row.provider = self.provider
            row.model = self.model
            row.api_key = self.api_key
            row.batch_size = self.batch_size
            row.normalize = self.normalize
            row.cache = self.cache
            row.connected = self.connected
            row.dimension = self.dimension

            db.commit()
        finally:
            db.close()

    @classmethod
    def load(cls, user_id: int = 1) -> "EmbeddingConfig":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(EmbeddingStateModel).filter(EmbeddingStateModel.id == user_id).first()
            if row is None:
                legacy_state = _load_legacy_json()
                if legacy_state is not None and user_id == 1:
                    legacy_state.save(user_id=user_id)
                    return legacy_state
                return cls()

            return cls(
                provider=row.provider or "",
                model=row.model or "",
                api_key=row.api_key,
                batch_size=row.batch_size or 512,
                normalize=bool(row.normalize),
                cache=bool(row.cache),
                connected=bool(row.connected),
                dimension=row.dimension or 0,
            )
        except Exception:
            return cls()
        finally:
            db.close()


_active_embedding_loaded = False
active_embedding = EmbeddingConfig()


def ensure_active_embedding_loaded(user_id: int = 1) -> EmbeddingConfig:
    """Lazily load active embedding state from DB on first use."""
    global _active_embedding_loaded

    if _active_embedding_loaded:
        return active_embedding

    loaded = EmbeddingConfig.load(user_id=user_id)
    active_embedding.provider = loaded.provider
    active_embedding.model = loaded.model
    active_embedding.api_key = loaded.api_key
    active_embedding.batch_size = loaded.batch_size
    active_embedding.normalize = loaded.normalize
    active_embedding.cache = loaded.cache
    active_embedding.connected = loaded.connected
    active_embedding.dimension = loaded.dimension
    _active_embedding_loaded = True

    return active_embedding
