"""
Active embedding configuration — persisted to disk.

Set by POST /embeddings/connect/.
Loaded automatically on import so config survives server restarts.

Other modules consume it as:
    from src.pipeline.config.embedding_config import active_embedding
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# Stored next to this file so the path is always predictable
_CONFIG_FILE = Path(__file__).parent / "embedding_state.json"


@dataclass
class EmbeddingConfig:
    provider: str = ""
    model: str = ""
    api_key: Optional[str] = None
    batch_size: int = 512
    normalize: bool = False
    cache: bool = False
    connected: bool = False

    def save(self) -> None:
        """Write current state to disk."""
        _CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> "EmbeddingConfig":
        """Load state from disk; return defaults if file is missing or corrupt."""
        if not _CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()


# Module-level singleton — loaded from disk on first import
active_embedding = EmbeddingConfig.load()
