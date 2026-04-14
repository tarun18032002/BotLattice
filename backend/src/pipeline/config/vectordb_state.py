"""
Active Vector DB configuration persisted to disk.

Set by POST /vector-db/connect/ and loaded on startup/import.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

_CONFIG_FILE = Path(__file__).parent / "vectordb_state.json"


@dataclass
class VectorDBState:
    vectordb_type: str = "qdrant"
    url: Optional[str] = None
    api_key: Optional[str] = None
    distance_metric: str = "Cosine"
    hybrid_search: bool = False
    store_meta: bool = True
    connected: bool = False

    def save(self) -> None:
        _CONFIG_FILE.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> "VectorDBState":
        if not _CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            allowed = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**allowed)
        except Exception:
            return cls()


active_vectordb = VectorDBState.load()
