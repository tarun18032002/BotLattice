"""Active chunking configuration persisted in PostgreSQL."""

from dataclasses import dataclass, field
import json

from src.database.db import Base, SessionLocal, engine, repair_legacy_auth_foreign_keys
from src.database.models import ChunkingRequest as ChunkingRequestModel
from src.pipeline.config.enums import ChunkingType
from src.pipeline.config.schemas import ChunkingRequest


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)
    repair_legacy_auth_foreign_keys()


@dataclass
class ChunkingConfig:
    chunking_type: str = ChunkingType.sentence.value
    chunk_size: int = 512
    chunk_overlap: int = 50
    language: str = "python"
    chunk_lines: int = 40
    chunk_lines_overlap: int = 10
    chunk_sizes: list[int] = field(default_factory=lambda: [2048, 512, 128])

    def save(self, user_id: int) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(ChunkingRequestModel).filter(ChunkingRequestModel.id == user_id).first()
            if row is None:
                row = ChunkingRequestModel(id=user_id)
                db.add(row)

            row.chunking_type = self.chunking_type
            row.chunk_size = int(self.chunk_size)
            row.chunk_overlap = int(self.chunk_overlap)
            row.language = self.language
            row.chunk_lines = int(self.chunk_lines)
            row.chunk_lines_overlap = int(self.chunk_lines_overlap)
            row.chunk_sizes = json.dumps(self.chunk_sizes)

            db.commit()
        finally:
            db.close()

    @classmethod
    def from_request(cls, req: ChunkingRequest) -> "ChunkingConfig":
        return cls(
            chunking_type=req.chunking_type.value,
            chunk_size=req.chunk_size or 512,
            chunk_overlap=req.chunk_overlap or 50,
            language=req.language or "python",
            chunk_lines=req.chunk_lines or 40,
            chunk_lines_overlap=req.chunk_lines_overlap or 10,
            chunk_sizes=req.chunk_sizes or [2048, 512, 128],
        )

    @classmethod
    def exists(cls, user_id: int) -> bool:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(ChunkingRequestModel).filter(ChunkingRequestModel.id == user_id).first()
            return row is not None
        finally:
            db.close()

    @classmethod
    def load(cls, user_id: int) -> "ChunkingConfig":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(ChunkingRequestModel).filter(ChunkingRequestModel.id == user_id).first()
            if row is None:
                return cls()

            parsed_chunk_sizes = [2048, 512, 128]
            try:
                raw_sizes = json.loads(row.chunk_sizes) if row.chunk_sizes else [2048, 512, 128]
                if isinstance(raw_sizes, list) and raw_sizes:
                    parsed_chunk_sizes = [int(x) for x in raw_sizes]
            except Exception:
                parsed_chunk_sizes = [2048, 512, 128]

            return cls(
                chunking_type=row.chunking_type.value if hasattr(row.chunking_type, "value") else str(row.chunking_type),
                chunk_size=row.chunk_size or 512,
                chunk_overlap=row.chunk_overlap or 50,
                language=row.language or "python",
                chunk_lines=row.chunk_lines or 40,
                chunk_lines_overlap=row.chunk_lines_overlap or 10,
                chunk_sizes=parsed_chunk_sizes,
            )
        except Exception:
            return cls()
        finally:
            db.close()

    def to_request(self) -> ChunkingRequest:
        return ChunkingRequest(
            chunking_type=ChunkingType(self.chunking_type),
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            language=self.language,
            chunk_lines=self.chunk_lines,
            chunk_lines_overlap=self.chunk_lines_overlap,
            chunk_sizes=self.chunk_sizes,
        )


active_chunking = ChunkingConfig()
