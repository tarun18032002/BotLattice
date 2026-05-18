"""Active Vector DB configuration persisted in PostgreSQL."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional

from src.database.db import Base, SessionLocal, engine
from src.database.models import VectorDBState as VectorDBStateModel


_LEGACY_CONFIG_FILE = Path(__file__).parent / "vectordb_state.json"


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _load_legacy_json() -> "VectorDBState | None":
    if not _LEGACY_CONFIG_FILE.exists():
        return None

    try:
        data = json.loads(_LEGACY_CONFIG_FILE.read_text(encoding="utf-8"))
        allowed = {k: v for k, v in data.items() if k in VectorDBState.__dataclass_fields__}
        return VectorDBState(**allowed)
    except Exception:
        return None


@dataclass
class VectorDBState:
    vectordb_type: str = "qdrant"
    url: Optional[str] = None
    api_key: Optional[str] = None
    distance_metric: str = "Cosine"
    hybrid_search: bool = False
    store_meta: bool = True
    connected: bool = False

    def save(self, user_id: int = 1) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(VectorDBStateModel).filter(
                VectorDBStateModel.id == user_id
            ).first()

            if row is None:
                row = VectorDBStateModel(id=user_id)
                db.add(row)

            row.vectordb_type = self.vectordb_type
            row.url = self.url
            row.api_key = self.api_key
            row.distance_metric = self.distance_metric
            row.hybrid_search = self.hybrid_search
            row.store_meta = self.store_meta
            row.connected = self.connected

            db.commit()
        finally:
            db.close()

    @classmethod
    def load(cls, user_id: int = 1) -> "VectorDBState":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(VectorDBStateModel).filter(VectorDBStateModel.id == user_id).first()
            if row is None:
                legacy_state = _load_legacy_json()
                if legacy_state is not None:
                    legacy_state.save(user_id=user_id)
                    return legacy_state
                return cls()

            return cls(
                vectordb_type=row.vectordb_type or "qdrant",
                url=row.url,
                api_key=row.api_key,
                distance_metric=row.distance_metric or "Cosine",
                hybrid_search=bool(row.hybrid_search),
                store_meta=bool(row.store_meta),
                connected=bool(row.connected),
            )
        except Exception:
            return cls()
        finally:
            db.close()


_active_vectordb_loaded = False
active_vectordb = VectorDBState()


def ensure_active_vectordb_loaded(user_id: int = 1) -> VectorDBState:
    """Lazily load active vector DB state from DB on first use."""
    global _active_vectordb_loaded

    if _active_vectordb_loaded:
        return active_vectordb

    loaded = VectorDBState.load(user_id=user_id)
    active_vectordb.vectordb_type = loaded.vectordb_type
    active_vectordb.url = loaded.url
    active_vectordb.api_key = loaded.api_key
    active_vectordb.distance_metric = loaded.distance_metric
    active_vectordb.hybrid_search = loaded.hybrid_search
    active_vectordb.store_meta = loaded.store_meta
    active_vectordb.connected = loaded.connected
    _active_vectordb_loaded = True

    return active_vectordb
