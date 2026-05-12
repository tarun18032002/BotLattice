from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Optional

from src.database.option_catalog import (
    SUPPORTED_KEYS,
    delete_provider_option,
    get_option,
    upsert_provider_option,
)
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


class ProviderOptionUpsert(BaseModel):
    label: Optional[str] = None
    models: Optional[list[str]] = None
    requires_api_key: Optional[bool] = None
    show_api_key: Optional[bool] = None
    url_placeholder: Optional[str] = None
    supports: Optional[dict[str, bool]] = None


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, int(value)))


def _clamp_float(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


@router.get("/settings/current/")
def get_current_settings():
    return active_llm_settings.to_dict()


@router.get("/settings/options/")
def get_settings_options():
    providers = get_option("llm_providers", fallback={})
    if not isinstance(providers, dict):
        providers = {}
    return {"llm_providers": providers}


@router.get("/settings/options/{key}/")
def get_any_options(key: str):
    if key not in SUPPORTED_KEYS:
        raise HTTPException(status_code=400, detail=f"Unsupported options key: {key}")

    data = get_option(key, fallback={})
    if not isinstance(data, dict):
        data = {}
    return {key: data}


@router.put("/settings/options/{key}/{provider}/")
def upsert_any_option(key: str, provider: str, req: ProviderOptionUpsert):
    if key not in SUPPORTED_KEYS:
        raise HTTPException(status_code=400, detail=f"Unsupported options key: {key}")

    payload = req.model_dump(exclude_none=True)
    ok = upsert_provider_option(key=key, provider=provider, payload=payload)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to upsert provider option")

    return {
        "status": "upserted",
        "key": key,
        "provider": provider,
        "data": get_option(key, fallback={}).get(provider.lower(), {}),
    }


@router.delete("/settings/options/{key}/{provider}/")
def delete_any_option(key: str, provider: str):
    if key not in SUPPORTED_KEYS:
        raise HTTPException(status_code=400, detail=f"Unsupported options key: {key}")

    ok = delete_provider_option(key=key, provider=provider)
    if not ok:
        raise HTTPException(status_code=404, detail="Provider option not found")

    return {
        "status": "deleted",
        "key": key,
        "provider": provider,
    }


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