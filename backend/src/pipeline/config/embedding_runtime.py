import threading


_EMBED_LOCK = threading.Lock()
_EMBED_READY = False


def _restore_embed_model_once() -> bool:
    from src.pipeline.config.embedding_config import ensure_active_embedding_loaded
    from src.pipeline.config.embedding_factory import create_embed_model
    from src.pipeline.config.dimension_extractor import validate_and_get_dimension
    from llama_index.core import Settings

    active_embedding = ensure_active_embedding_loaded()

    if not active_embedding.connected:
        return False

    provider = active_embedding.provider
    model = active_embedding.model
    api_key = active_embedding.api_key

    embed_model = create_embed_model(
        provider=provider,
        model=model,
        api_key=api_key,
        batch_size=active_embedding.batch_size,
        normalize=active_embedding.normalize,
        cache=active_embedding.cache,
    )
    
    Settings.embed_model = embed_model
    
    # Dynamically extract dimension on startup to ensure it's always current
    dimension = validate_and_get_dimension(embed_model)
    if dimension != active_embedding.dimension:
        print(f"[startup] Updating dimension from {active_embedding.dimension} to {dimension}")
        active_embedding.dimension = dimension
        active_embedding.save()
    
    print(f"[startup] Restored embed model: {provider}/{model} (dimension: {dimension})")
    return True


def ensure_embed_model_ready() -> None:
    """Load persisted embed model lazily (safe to call multiple times)."""
    global _EMBED_READY

    if _EMBED_READY:
        return

    with _EMBED_LOCK:
        if _EMBED_READY:
            return

        try:
            _EMBED_READY = _restore_embed_model_once()
        except Exception as exc:
            print(f"[startup] Could not restore embed model: {exc}")


def warm_embed_model_in_background() -> None:
    """Kick off non-blocking embed model warm-up during app startup."""

    thread = threading.Thread(target=ensure_embed_model_ready, daemon=True)
    thread.start()
