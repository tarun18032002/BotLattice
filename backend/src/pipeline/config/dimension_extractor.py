"""Utility to dynamically extract dimensions from different embedding models."""

from typing import Optional


def get_embedding_dimension(embed_model) -> int:
    """
    Dynamically extract dimension from an embedding model.
    
    Supports multiple embedding providers and their various attribute names.
    Falls back to a generic test embedding if standard attributes aren't available.
    
    Args:
        embed_model: An instantiated embedding model (FastEmbed, OpenAI, etc.)
    
    Returns:
        The embedding dimension (integer)
    """
    
    # Try common dimension attribute names across different providers
    dimension_attrs = [
        "embed_dim",           # llama_index standard
        "embedding_dimension", # alternative naming
        "dimension",           # direct naming
        "dim",                 # shorthand
        "_embed_dim",          # private attribute
        "model_dim",           # model-specific
    ]
    
    # Try direct attribute access
    for attr in dimension_attrs:
        if hasattr(embed_model, attr):
            try:
                dim = getattr(embed_model, attr)
                if isinstance(dim, int) and dim > 0:
                    return dim
            except Exception:
                pass
    
    # Try getting from model config/info if available
    if hasattr(embed_model, "model_info"):
        try:
            if isinstance(embed_model.model_info, dict) and "dimension" in embed_model.model_info:
                return embed_model.model_info["dimension"]
        except Exception:
            pass
    
    # Fallback: try embedding a test string to determine dimension
    try:
        test_embedding = embed_model.get_text_embedding("test")
        if isinstance(test_embedding, (list, tuple)) and len(test_embedding) > 0:
            return len(test_embedding)
    except Exception:
        pass
    
    # Last resort: check model name for known defaults
    if hasattr(embed_model, "model_name"):
        model_name = embed_model.model_name.lower()
        
        # OpenAI models
        if "text-embedding-3-small" in model_name:
            return 1536
        elif "text-embedding-3-large" in model_name:
            return 3072
        elif "text-embedding-ada-002" in model_name:
            return 1536
        
        # Google models
        elif "embedding-001" in model_name:
            return 768
        
        # Common HuggingFace/FastEmbed models
        elif "multilingual-e5-large" in model_name:
            return 1024
        elif "multilingual-e5-base" in model_name:
            return 768
        elif "all-minilm-l6-v2" in model_name:
            return 384
        elif "all-mpnet-base-v2" in model_name:
            return 768
    
    # Ultimate fallback (should rarely reach here)
    return 384


def validate_and_get_dimension(embed_model) -> int:
    """
    Safely extract and validate embedding dimension.
    Logs warnings if dimension extraction is uncertain.
    
    Args:
        embed_model: An instantiated embedding model
    
    Returns:
        The embedding dimension (guaranteed positive integer)
    """
    try:
        dimension = get_embedding_dimension(embed_model)
        if dimension > 0:
            return dimension
    except Exception as exc:
        print(f"Warning: Error extracting embedding dimension: {exc}")
    
    # Safe fallback
    print("Warning: Using fallback dimension 384")
    return 384
