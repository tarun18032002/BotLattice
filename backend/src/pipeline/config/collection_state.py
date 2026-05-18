"""Active collection configuration persisted in PostgreSQL."""

from dataclasses import dataclass

from src.database.db import Base, SessionLocal, engine, repair_legacy_auth_foreign_keys
from src.database.models import CollectionState as CollectionStateModel
from src.pipeline.config.enums import CollectionMode
from src.pipeline.config.schemas import CollectionRequest


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)
    repair_legacy_auth_foreign_keys()


@dataclass
class CollectionConfig:
    mode: str = CollectionMode.APPEND_TO_EXISTING.value
    collection_name: str = "documents"
    description: str | None = None
    tags: str | None = None

    def save(self, user_id: int) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(CollectionStateModel).filter(CollectionStateModel.id == user_id).first()
            if row is None:
                row = CollectionStateModel(id=user_id)
                db.add(row)

            row.mode = self.mode
            row.collection_name = self.collection_name
            row.description = self.description
            row.tags = self.tags

            db.commit()
        finally:
            db.close()

    @classmethod
    def from_request(cls, req: CollectionRequest) -> "CollectionConfig":
        return cls(
            mode=req.mode.value,
            collection_name=req.collection_name,
            description=req.description,
            tags=req.tags,
        )

    @classmethod
    def exists(cls, user_id: int) -> bool:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(CollectionStateModel).filter(CollectionStateModel.id == user_id).first()
            return row is not None
        finally:
            db.close()

    @classmethod
    def load(cls, user_id: int) -> "CollectionConfig":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(CollectionStateModel).filter(CollectionStateModel.id == user_id).first()
            if row is None:
                return cls()

            return cls(
                mode=row.mode or CollectionMode.APPEND_TO_EXISTING.value,
                collection_name=row.collection_name or "documents",
                description=row.description,
                tags=row.tags,
            )
        except Exception:
            return cls()
        finally:
            db.close()

    def to_request(self) -> CollectionRequest:
        return CollectionRequest(
            mode=CollectionMode(self.mode),
            collection_name=self.collection_name,
            description=self.description,
            tags=self.tags,
        )


active_collection = CollectionConfig()
