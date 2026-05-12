# connecting to local or remote embeddings models

from fastapi import APIRouter, HTTPException
from typing import Optional

from llama_index.core import Settings
from src.database.option_catalog import get_option
from src.pipeline.config.embedding_config import active_embedding
from src.pipeline.config.embedding_factory import create_embed_model

router = APIRouter()

def _providers() -> dict:
    providers = get_option("embedding_providers", fallback={})
    return providers if isinstance(providers, dict) else {}


@router.get("/embeddings/providers/")
def get_embedding_providers():
    return _providers()


@router.get("/embeddings/current/")
def get_current_embedding():
    """Return the active embedding config set by /embeddings/connect/."""
    if not active_embedding.connected:
        raise HTTPException(status_code=404, detail="No embedding model connected yet.")
    return {
        "provider":   active_embedding.provider,
        "model":      active_embedding.model,
        "batch_size": active_embedding.batch_size,
        "normalize":  active_embedding.normalize,
        "cache":      active_embedding.cache,
    }


@router.post("/embeddings/connect/")
def connect_embeddings(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    batch_size: Optional[int] = 512,
    normalize: Optional[bool] = False,
    cache: Optional[bool] = False,
):
    # ── 1. Validate provider ──────────────────────────────────────────────────
    providers = _providers()

    if provider not in providers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider}'. Choose from: {list(providers.keys())}",
        )

    provider_info = providers[provider]
    effective_api_key = api_key

    # Reuse previously saved API key for the same provider so users are not
    # forced to re-enter secrets when only changing model/options.
    if (
        not effective_api_key
        and active_embedding.connected
        and active_embedding.provider == provider
        and active_embedding.api_key
    ):
        effective_api_key = active_embedding.api_key

    # ── 2. Validate model belongs to that provider ────────────────────────────
    if model not in provider_info["models"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Model '{model}' is not available for provider '{provider}'. "
                f"Available models: {provider_info['models']}"
            ),
        )

    # ── 3. Validate API key is supplied when required ─────────────────────────
    if provider_info["requires_api_key"] and not effective_api_key:
        raise HTTPException(
            status_code=422,
            detail=f"Provider '{provider}' requires an API key.",
        )

    # ── 4. Live connection test + build embed model ───────────────────────────
    try:
        if provider == "huggingface":
            embed_model = create_embed_model(
                provider=provider,
                model=model,
                api_key=api_key,
                batch_size=batch_size,
                normalize=normalize,
                cache=cache,
            )
            Settings.embed_model = embed_model

        elif provider == "openai":
            from openai import OpenAI
            # Validate key with a cheap live call first
            OpenAI(api_key=effective_api_key).embeddings.create(input=["test"], model=model)
            embed_model = create_embed_model(
                provider=provider,
                model=model,
                api_key=effective_api_key,
                batch_size=batch_size,
                normalize=normalize,
                cache=cache,
            )
            Settings.embed_model = embed_model

        elif provider == "google":
            import importlib
            genai = importlib.import_module("google.generativeai")
            genai.configure(api_key=effective_api_key)
            genai.embed_content(model=model, content="test")
            embed_model = create_embed_model(
                provider=provider,
                model=model,
                api_key=effective_api_key,
                batch_size=batch_size,
                normalize=normalize,
                cache=cache,
            )
            Settings.embed_model = embed_model

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Connection to '{provider}/{model}' failed: {exc}",
        )

    # ── 5. Persist config so other APIs can read it (survives restarts) ────────
    active_embedding.provider   = provider
    active_embedding.model      = model
    active_embedding.api_key    = effective_api_key
    active_embedding.batch_size = batch_size
    active_embedding.normalize  = normalize
    active_embedding.cache      = cache
    active_embedding.connected  = True
    
    # Extract actual dimension from the loaded embed model
    try:
        active_embedding.dimension = embed_model.embed_dim
    except Exception as exc:
        print(f"Warning: Could not extract dimension from embed model: {exc}")
        active_embedding.dimension = 384  # fallback
    
    active_embedding.save()  # write to embedding_state.json

    return {
        "status": "connected",
        "provider": provider,
        "model": model,
        "batch_size": batch_size,
        "normalize": normalize,
        "cache": cache,
        "dimension": active_embedding.dimension,
    }

