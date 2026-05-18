from fastapi import APIRouter, Depends

from src.pipeline.config.chunking_config import CHUNKING_OPTIONS
from src.pipeline.config.schemas import ChunkingType, ChunkingRequest, CollectionRequest
from src.pipeline.config.chunking_state import ChunkingConfig
from src.pipeline.config.collection_state import CollectionConfig
from src.database.models import AuthUser
from src.api.routes_auth import get_current_auth_user

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


@router.get("/chunking/current/")
def get_current_chunking(current_user: AuthUser = Depends(get_current_auth_user)):
    chunking = ChunkingConfig.load(user_id=current_user.id)
    return chunking.to_request().model_dump()


@router.post("/chunking/save/")
def save_chunking(req: ChunkingRequest, current_user: AuthUser = Depends(get_current_auth_user)):
    state = ChunkingConfig.from_request(req)
    state.save(user_id=current_user.id)
    return {
        "status": "saved",
        "chunking": state.to_request().model_dump(),
    }


@router.get("/collection/current/")
def get_current_collection(current_user: AuthUser = Depends(get_current_auth_user)):
    collection = CollectionConfig.load(user_id=current_user.id)
    return collection.to_request().model_dump()


@router.post("/collection/save/")
def save_collection(req: CollectionRequest, current_user: AuthUser = Depends(get_current_auth_user)):
    state = CollectionConfig.from_request(req)
    state.save(user_id=current_user.id)
    return {
        "status": "saved",
        "collection": state.to_request().model_dump(),
    }