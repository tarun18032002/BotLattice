from fastapi import APIRouter

from src.pipeline.config.chunking_config import CHUNKING_OPTIONS
from src.pipeline.config.schemas import ChunkingType

router = APIRouter()


@router.get("/chunking/options/{chunking_type}")
def get_chunking_options(chunking_type:ChunkingType):
    key = chunking_type.value  # safer

    if key not in CHUNKING_OPTIONS:
        return {"error": "Invalid chunking type"}

    return {
        "type": key,
        **CHUNKING_OPTIONS[key]
    }