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

    def save(self, user_id: int = 1) -> None:
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(LLMSettingsStateModel).filter(LLMSettingsStateModel.id == user_id).first()
            if row is None:
                row = LLMSettingsStateModel(id=user_id, systemPrompt=_DEFAULT_SYSTEM_PROMPT)
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
    def load(cls, user_id: int = 1) -> "LLMSettingsState":
        _ensure_tables()
        db = SessionLocal()
        try:
            row = db.query(LLMSettingsStateModel).filter(LLMSettingsStateModel.id == user_id).first()
            if row is None:
                legacy_state = _load_legacy_json()
                if legacy_state is not None and user_id == 1:
                    legacy_state.save(user_id=user_id)
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


_active_llm_settings_loaded = False
active_llm_settings = LLMSettingsState()


def ensure_active_llm_settings_loaded(user_id: int = 1) -> LLMSettingsState:
    """Lazily load active LLM settings from DB on first use."""
    global _active_llm_settings_loaded

    if _active_llm_settings_loaded:
        return active_llm_settings

    loaded = LLMSettingsState.load(user_id=user_id)
    active_llm_settings.llmProvider = loaded.llmProvider
    active_llm_settings.llmModel = loaded.llmModel
    active_llm_settings.apiKey = loaded.apiKey
    active_llm_settings.temperature = loaded.temperature
    active_llm_settings.maxTokens = loaded.maxTokens
    active_llm_settings.defaultTopK = loaded.defaultTopK
    active_llm_settings.simThreshold = loaded.simThreshold
    active_llm_settings.reranking = loaded.reranking
    active_llm_settings.multiQuery = loaded.multiQuery
    active_llm_settings.compression = loaded.compression
    active_llm_settings.showSources = loaded.showSources
    active_llm_settings.streamResponses = loaded.streamResponses
    active_llm_settings.systemPrompt = loaded.systemPrompt
    _active_llm_settings_loaded = True

    return active_llm_settings