"""Active LLM and retrieval settings persisted in PostgreSQL."""

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Optional

from src.database.db import Base, SessionLocal, engine
from src.database.models import LLMSettingsState as LLMSettingsStateModel

_LEGACY_CONFIG_FILE = Path(__file__).parent / "llm_settings_state.json"


def _ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _load_legacy_json() -> "LLMSettingsState | None":
    if not _LEGACY_CONFIG_FILE.exists():
        return None

    try:
        data = json.loads(_LEGACY_CONFIG_FILE.read_text(encoding="utf-8"))
        allowed = {k: v for k, v in data.items() if k in LLMSettingsState.__dataclass_fields__}
        return LLMSettingsState(**allowed)
    except Exception:
        return None

_DEFAULT_SYSTEM_PROMPT = (
    "You are a precise RAG assistant with access to a knowledge base.\n\n"
    "Rules:\n"
    "1. Answer only from the retrieved context when in RAG mode\n"
    "2. If context is insufficient, say so clearly\n"
    "3. Always cite source documents when possible\n"
    "4. Be concise and structured in your responses"
)


@dataclass
class LLMSettingsState:
    llmProvider: str = "anthropic"
    llmModel: str = "claude-sonnet-4-20250514"
    apiKey: Optional[str] = None
    temperature: float = 0.2
    maxTokens: int = 1024
    defaultTopK: int = 5
    simThreshold: float = 0.75
    reranking: bool = False
    multiQuery: bool = True
    compression: bool = False
    showSources: bool = True
    streamResponses: bool = False
    systemPrompt: str = _DEFAULT_SYSTEM_PROMPT

    def save(self) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(LLMSettingsStateModel).filter(LLMSettingsStateModel.id == 1).first()
            if row is None:
                row = LLMSettingsStateModel(id=1, systemPrompt=_DEFAULT_SYSTEM_PROMPT)
                db.add(row)

            row.llmProvider = self.llmProvider
            row.llmModel = self.llmModel
            row.apiKey = self.apiKey
            row.temperature = self.temperature
            row.maxTokens = self.maxTokens
            row.defaultTopK = self.defaultTopK
            row.simThreshold = self.simThreshold
            row.reranking = self.reranking
            row.multiQuery = self.multiQuery
            row.compression = self.compression
            row.showSources = self.showSources
            row.streamResponses = self.streamResponses
            row.systemPrompt = self.systemPrompt

            db.commit()
        finally:
            db.close()

    def to_dict(self) -> dict:
        return asdict(self)

    def update_from_dict(self, patch: dict) -> None:
        for key, value in patch.items():
            if key in self.__dataclass_fields__:
                setattr(self, key, value)

    @classmethod
    def load(cls) -> "LLMSettingsState":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(LLMSettingsStateModel).filter(LLMSettingsStateModel.id == 1).first()
            if row is None:
                legacy_state = _load_legacy_json()
                if legacy_state is not None:
                    legacy_state.save()
                    return legacy_state
                return cls()

            return cls(
                llmProvider=row.llmProvider or "anthropic",
                llmModel=row.llmModel or "claude-sonnet-4-20250514",
                apiKey=row.apiKey,
                temperature=row.temperature if row.temperature is not None else 0.2,
                maxTokens=row.maxTokens or 1024,
                defaultTopK=row.defaultTopK or 5,
                simThreshold=row.simThreshold if row.simThreshold is not None else 0.75,
                reranking=bool(row.reranking),
                multiQuery=bool(row.multiQuery),
                compression=bool(row.compression),
                showSources=bool(row.showSources),
                streamResponses=bool(row.streamResponses),
                systemPrompt=row.systemPrompt or _DEFAULT_SYSTEM_PROMPT,
            )
        except Exception:
            return cls()
        finally:
            db.close()


active_llm_settings = LLMSettingsState.load()