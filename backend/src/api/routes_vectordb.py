from fastapi import APIRouter
from typing import Optional

from src.pipeline.config.vectordb_config import VECTORDB_OPTIONS
from src.pipeline.config.schemas import VectorDBType
from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.settings import vectordb

router = APIRouter()


@router.get("/vectordb/options/{chunking_type}")
def get_vectordb_options(vectordb_type:VectorDBType):
    key = vectordb_type.value  # safer

    if key not in VECTORDB_OPTIONS:
        return {"error": "Invalid chunking type"}

    return {
        "type": key,
        **VECTORDB_OPTIONS[key]
    }


@router.get("/vector-db/collections")
def get_collections():
    """
    Fetch collections from the configured vector database
    """

    return {
        "vector_db": vectordb.vectordb_type.value,
        "collections": VectorDBFactory.get_collections(vectordb.vectordb_type)
    }