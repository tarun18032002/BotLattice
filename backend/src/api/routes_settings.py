from fastapi import APIRouter, HTTPException
from fastapi import Depends

from src.database.option_catalog import (
    SUPPORTED_KEYS,
    delete_provider_option,
    get_option,
    upsert_provider_option,
)
from src.pipeline.config.llm_settings_state import ensure_active_llm_settings_loaded
from src.database.schema import SettingsPatch,ProviderOptionUpsert
from src.database.models import AuthUser
from src.api.routes_auth import get_current_auth_user

router = APIRouter()



def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, int(value)))


def _clamp_float(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


@router.get("/settings/current/")
def get_current_settings(current_user: AuthUser = Depends(get_current_auth_user)):
    settings_state = ensure_active_llm_settings_loaded(user_id=current_user.id)
    return settings_state.to_dict()


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
def save_settings(req: SettingsPatch, current_user: AuthUser = Depends(get_current_auth_user)):
    patch = req.model_dump(exclude_none=True)
    settings_state = ensure_active_llm_settings_loaded(user_id=current_user.id)

    if "temperature" in patch:
        patch["temperature"] = _clamp_float(patch["temperature"], 0.0, 1.0)

    if "maxTokens" in patch:
        patch["maxTokens"] = _clamp_int(patch["maxTokens"], 64, 16384)

    if "defaultTopK" in patch:
        patch["defaultTopK"] = _clamp_int(patch["defaultTopK"], 1, 20)

    if "simThreshold" in patch:
        patch["simThreshold"] = _clamp_float(patch["simThreshold"], 0.0, 1.0)

    settings_state.update_from_dict(patch)
    settings_state.save(user_id=current_user.id)

    return {
        "status": "saved",
        "settings": settings_state.to_dict(),
    }