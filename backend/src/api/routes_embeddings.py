# connecting to local or remote embeddings models

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from llama_index.core import Settings
from src.api.routes_auth import get_current_auth_user
from src.database.models import AuthUser
from src.database.option_catalog import get_option
from src.pipeline.config.embedding_config import EmbeddingConfig, active_embedding, ensure_active_embedding_loaded
from src.pipeline.config.embedding_factory import create_embed_model
from src.pipeline.config.dimension_extractor import validate_and_get_dimension

router = APIRouter()

def _providers() -> dict:
    providers = get_option("embedding_providers", fallback={})
    return providers if isinstance(providers, dict) else {}


@router.get("/embeddings/providers/")
def get_embedding_providers():
    return _providers()


@router.get("/embeddings/current/")
def get_current_embedding(current_user: AuthUser = Depends(get_current_auth_user)):
    """Return the active embedding config set by /embeddings/connect/."""
    user_embedding = EmbeddingConfig.load(user_id=current_user.id)

    if not user_embedding.connected:
        return {
            "connected": False,
            "provider": "",
            "model": "",
            "batch_size": 512,
            "normalize": False,
            "cache": False,
            "dimension": 0,
        }

    return {
        "connected":  True,
        "provider":   user_embedding.provider,
        "model":      user_embedding.model,
        "batch_size": user_embedding.batch_size,
        "normalize":  user_embedding.normalize,
        "cache":      user_embedding.cache,
        "dimension":  user_embedding.dimension,
    }


@router.post("/embeddings/sync-dimension/")
def sync_embedding_dimension(current_user: AuthUser = Depends(get_current_auth_user)):
    """
    Sync/update the embedding dimension from the currently connected model.
    
    Useful if the stored dimension becomes out-of-sync with the actual model.
    Returns the current dimension value stored in the database.
    """
    user_embedding = EmbeddingConfig.load(user_id=current_user.id)
    ensure_active_embedding_loaded(user_id=current_user.id)

    if not user_embedding.connected:
        raise HTTPException(
            status_code=404,
            detail="No embedding model connected yet."
        )
    
    from llama_index.core import Settings
    
    embed_model = Settings.embed_model
    if embed_model is None:
        raise HTTPException(
            status_code=500,
            detail="Embedding model is not loaded in memory."
        )
    
    # Extract current dimension
    current_dimension = validate_and_get_dimension(embed_model)
    old_dimension = user_embedding.dimension
    
    # Update if changed
    if current_dimension != old_dimension:
        user_embedding.dimension = current_dimension
        user_embedding.save(user_id=current_user.id)

        # Keep runtime singleton in sync for in-process consumers.
        active_embedding.dimension = current_dimension

        return {
            "status": "synced",
            "old_dimension": old_dimension,
            "new_dimension": current_dimension,
            "provider": user_embedding.provider,
            "model": user_embedding.model,
        }
    else:
        return {
            "status": "already_synced",
            "dimension": current_dimension,
            "provider": user_embedding.provider,
            "model": user_embedding.model,
        }


@router.post("/embeddings/connect/")
def connect_embeddings(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    batch_size: Optional[int] = 512,
    normalize: Optional[bool] = False,
    cache: Optional[bool] = False,
    current_user: AuthUser = Depends(get_current_auth_user),
):
    print(f"Connecting to embedding provider '{provider}' with model '{model}' for user_id={current_user.id}")
    # ── 1. Validate provider ──────────────────────────────────────────────────
    providers = _providers()

    if provider not in providers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider}'. Choose from: {list(providers.keys())}",
        )

    provider_info = providers[provider]
    effective_api_key = api_key
    user_embedding = EmbeddingConfig.load(user_id=current_user.id)
    ensure_active_embedding_loaded(user_id=current_user.id)

    # Reuse previously saved API key for the same provider so users are not
    # forced to re-enter secrets when only changing model/options.
    if (
        not effective_api_key
        and user_embedding.connected
        and user_embedding.provider == provider
        and user_embedding.api_key
    ):
        effective_api_key = user_embedding.api_key

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
                api_key=effective_api_key,
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

    user_embedding.provider   = provider
    user_embedding.model      = model
    user_embedding.api_key    = effective_api_key
    user_embedding.batch_size = batch_size
    user_embedding.normalize  = normalize
    user_embedding.cache      = cache
    user_embedding.connected  = True
    
    # Dynamically extract actual dimension from the loaded embed model
    user_embedding.dimension = validate_and_get_dimension(embed_model)
    
    user_embedding.save(user_id=current_user.id)

    # Keep runtime singleton in sync for in-process consumers.
    active_embedding.provider = user_embedding.provider
    active_embedding.model = user_embedding.model
    active_embedding.api_key = user_embedding.api_key
    active_embedding.batch_size = user_embedding.batch_size
    active_embedding.normalize = user_embedding.normalize
    active_embedding.cache = user_embedding.cache
    active_embedding.connected = user_embedding.connected
    active_embedding.dimension = user_embedding.dimension

    return {
        "status": "connected",
        "provider": provider,
        "model": model,
        "batch_size": batch_size,
        "normalize": normalize,
        "cache": cache,
        "dimension": user_embedding.dimension,
    }


