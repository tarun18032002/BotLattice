from fastapi import APIRouter, HTTPException
from typing import Optional
import qdrant_client

from src.pipeline.config.vectordb_config import VECTORDB_OPTIONS
from src.pipeline.config.schemas import VectorDBType
from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.settings import vectordb
from src.pipeline.config.vectordb_state import active_vectordb

router = APIRouter()

VECTORDB_PROVIDERS = {
    "qdrant": {
        "requires_api_key": False,
        "show_api_key": True,
        "url_placeholder": "http://localhost:6333",
        "supports": {
            "distance_metric": True,
            "hybrid_search": True,
            "store_meta": True,
        },
    }
}


@router.get("/vector-db/options/{chunking_type}")
def get_vectordb_options(vectordb_type:VectorDBType):
    key = vectordb_type.value  # safer

    if key not in VECTORDB_OPTIONS:
        return {"error": "Invalid chunking type"}

    return {
        "type": key,
        **VECTORDB_OPTIONS[key]
    }


def _qdrant_client():
    """Return a Qdrant client using the active connection config."""
    url = active_vectordb.url or "http://localhost:6333"
    api_key = active_vectordb.api_key or None
    return qdrant_client.QdrantClient(url=url, api_key=api_key)


def _collection_detail(client, name: str) -> dict:
    """Return a metadata dict for a single Qdrant collection."""
    try:
        info = client.get_collection(collection_name=name)
        vectors_cfg = info.config.params.vectors
        if hasattr(vectors_cfg, "size"):
            dim = int(vectors_cfg.size)
            distance = str(vectors_cfg.distance.name if hasattr(vectors_cfg.distance, "name") else vectors_cfg.distance)
        elif isinstance(vectors_cfg, dict) and vectors_cfg:
            first = next(iter(vectors_cfg.values()))
            dim = int(first.size) if hasattr(first, "size") else 0
            distance = str(first.distance.name if hasattr(first.distance, "name") else first.distance) if hasattr(first, "distance") else "Unknown"
        else:
            dim, distance = 0, "Unknown"

        points_count = info.points_count or 0
        return {
            "name": name,
            "chunks": points_count,
            "docs": 0,                    # Qdrant has no native doc count; placeholder
            "db": "qdrant",
            "dim": dim,
            "distance": distance,
            "status": str(info.status.name if hasattr(info.status, "name") else info.status),
        }
    except Exception:
        return {"name": name, "chunks": 0, "docs": 0, "db": "qdrant", "dim": 0, "distance": "Unknown", "status": "unknown"}


@router.get("/vector-db/collections")
def get_collections():
    """Fetch all collections with per-collection metadata from Qdrant."""
    db_type = vectordb.vectordb_type
    try:
        client = _qdrant_client()
        names = [col.name for col in client.get_collections().collections]
        collections = [_collection_detail(client, n) for n in names]
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch collections: {exc}")

    return {"vector_db": db_type.value, "collections": collections}


@router.get("/vector-db/collections/{collection_name}")
def get_collection_detail(collection_name: str):
    """Return detailed metadata for a single collection."""
    try:
        client = _qdrant_client()
        return _collection_detail(client, collection_name)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch collection '{collection_name}': {exc}")


@router.delete("/vector-db/collections/{collection_name}")
def delete_collection(collection_name: str):
    """Permanently delete a collection from the vector database."""
    try:
        client = _qdrant_client()
        client.delete_collection(collection_name=collection_name)
        return {"status": "deleted", "collection": collection_name}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to delete collection '{collection_name}': {exc}")


@router.get("/vector-db/providers/")
def get_vectordb_providers():
    return VECTORDB_PROVIDERS


@router.get("/vector-db/current/")
def get_current_vectordb():
    if not active_vectordb.connected:
        raise HTTPException(status_code=404, detail="No vector DB connected yet.")

    return {
        "vectordb_type": active_vectordb.vectordb_type,
        "url": active_vectordb.url,
        "distance_metric": active_vectordb.distance_metric,
        "hybrid_search": active_vectordb.hybrid_search,
        "store_meta": active_vectordb.store_meta,
    }

@router.get("/vector-db/GetCurrentDB/")
def fetch_current_db():
    return get_current_vectordb()

@router.post("/vector-db/connect/")
def connect_vector_db(
    vectordb_type: VectorDBType,
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    distance_metric: Optional[str] = "Cosine",
    hybrid_search: Optional[bool] = False,
    store_meta: Optional[bool] = True,
):
    provider_key = vectordb_type.value

    if provider_key not in VECTORDB_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported vector DB '{provider_key}'.",
        )

    provider_info = VECTORDB_PROVIDERS[provider_key]
    effective_url = url or active_vectordb.url or provider_info["url_placeholder"]
    effective_api_key = api_key

    if (
        not effective_api_key
        and active_vectordb.connected
        and active_vectordb.vectordb_type == provider_key
        and active_vectordb.api_key
    ):
        effective_api_key = active_vectordb.api_key

    if provider_info["requires_api_key"] and not effective_api_key:
        raise HTTPException(
            status_code=422,
            detail=f"Vector DB '{provider_key}' requires an API key.",
        )

    # Live connection test
    try:
        if vectordb_type == VectorDBType.QDRANT:
            client = qdrant_client.QdrantClient(url=effective_url, api_key=effective_api_key)
            client.get_collections()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported vector DB '{provider_key}'.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Connection to '{provider_key}' failed: {exc}",
        )

    # Persist runtime state
    active_vectordb.vectordb_type = provider_key
    active_vectordb.url = effective_url
    active_vectordb.api_key = effective_api_key
    active_vectordb.distance_metric = distance_metric or "Cosine"
    active_vectordb.hybrid_search = bool(hybrid_search)
    active_vectordb.store_meta = bool(store_meta)
    active_vectordb.connected = True
    active_vectordb.save()

    # Sync in-memory request model used by existing pipeline imports
    vectordb.vectordb_type = vectordb_type
    vectordb.url = effective_url
    vectordb.api_key = effective_api_key

    return {
        "status": "connected",
        "vectordb_type": provider_key,
        "url": effective_url,
        "distance_metric": active_vectordb.distance_metric,
        "hybrid_search": active_vectordb.hybrid_search,
        "store_meta": active_vectordb.store_meta,
    }