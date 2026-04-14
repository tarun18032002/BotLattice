from inspect import signature
from pathlib import Path


def _supported_kwargs(cls, desired):
    """Keep only kwargs that the target class constructor supports."""
    params = set(signature(cls.__init__).parameters.keys())
    params.discard("self")
    return {k: v for k, v in desired.items() if k in params and v is not None}


def create_embed_model(
    provider: str,
    model: str,
    api_key=None,
    batch_size: int = 512,
    normalize: bool = False,
    cache: bool = False,
):
    """Instantiate a LlamaIndex embed model while safely applying optional knobs.

    Not all providers support all options, so kwargs are filtered at runtime.
    """
    common = {
        "model": model,
        "model_name": model,
        "api_key": api_key,
        "embed_batch_size": batch_size,
        "batch_size": batch_size,
        "normalize": normalize,
    }

    cache_dir = Path(".cache") / "embeddings"
    if cache:
        cache_dir.mkdir(parents=True, exist_ok=True)
        common["cache_dir"] = str(cache_dir)

    if provider == "huggingface":
        from llama_index.embeddings.fastembed import FastEmbedEmbedding
        kwargs = _supported_kwargs(FastEmbedEmbedding, common)
        return FastEmbedEmbedding(**kwargs)

    if provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding
        kwargs = _supported_kwargs(OpenAIEmbedding, common)
        return OpenAIEmbedding(**kwargs)

    if provider == "google":
        import importlib
        GoogleGenAIEmbedding = importlib.import_module(
            "llama_index.embeddings.google_genai"
        ).GoogleGenAIEmbedding
        kwargs = _supported_kwargs(GoogleGenAIEmbedding, common)
        return GoogleGenAIEmbedding(**kwargs)

    raise ValueError(f"Unsupported provider: {provider}")
