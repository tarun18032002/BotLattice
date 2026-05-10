from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from src.pipeline.config.llm_settings_state import active_llm_settings

router = APIRouter()


class SettingsPatch(BaseModel):
    llmProvider: Optional[str] = None
    llmModel: Optional[str] = None
    apiKey: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    defaultTopK: Optional[int] = None
    simThreshold: Optional[float] = None
    reranking: Optional[bool] = None
    multiQuery: Optional[bool] = None
    compression: Optional[bool] = None
    showSources: Optional[bool] = None
    streamResponses: Optional[bool] = None
    systemPrompt: Optional[str] = None


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, int(value)))


def _clamp_float(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


@router.get("/settings/current/")
def get_current_settings():
    return active_llm_settings.to_dict()


@router.post("/settings/save/")
def save_settings(req: SettingsPatch):
    patch = req.model_dump(exclude_none=True)

    if "temperature" in patch:
        patch["temperature"] = _clamp_float(patch["temperature"], 0.0, 1.0)

    if "maxTokens" in patch:
        patch["maxTokens"] = _clamp_int(patch["maxTokens"], 64, 16384)

    if "defaultTopK" in patch:
        patch["defaultTopK"] = _clamp_int(patch["defaultTopK"], 1, 20)

    if "simThreshold" in patch:
        patch["simThreshold"] = _clamp_float(patch["simThreshold"], 0.0, 1.0)

    active_llm_settings.update_from_dict(patch)
    active_llm_settings.save()

    return {
        "status": "saved",
        "settings": active_llm_settings.to_dict(),
    }