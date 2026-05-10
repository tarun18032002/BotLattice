"""
Active LLM and retrieval settings persisted to disk.

Used by the Settings UI and query pipeline so retrieval behavior matches UI
configuration and survives backend restarts.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

_CONFIG_FILE = Path(__file__).parent / "llm_settings_state.json"

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
        _CONFIG_FILE.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    def to_dict(self) -> dict:
        return asdict(self)

    def update_from_dict(self, patch: dict) -> None:
        for key, value in patch.items():
            if key in self.__dataclass_fields__:
                setattr(self, key, value)

    @classmethod
    def load(cls) -> "LLMSettingsState":
        if not _CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            allowed = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**allowed)
        except Exception:
            return cls()


active_llm_settings = LLMSettingsState.load()