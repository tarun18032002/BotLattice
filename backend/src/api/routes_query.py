from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from llama_index.core import Settings
from src.api.routes_auth import get_current_auth_user
from src.database.models import AuthUser
from src.pipeline.config.embedding_config import EmbeddingConfig
from src.pipeline.config.embedding_factory import create_embed_model
from src.pipeline.query.query_pipeline import run_query
from src.pipeline.config.enums import VectorDBType

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    collection_name: str
    top_k: Optional[int] = None
    retrieval_settings: Optional[dict] = None

@router.post("/query")
def query_rag(req: QueryRequest, current_user: AuthUser = Depends(get_current_auth_user)):
    try : 
        user_embedding = EmbeddingConfig.load(user_id=current_user.id)
        if not user_embedding.connected:
            raise HTTPException(status_code=400, detail="No embedding model connected for this user")

        Settings.embed_model = create_embed_model(
            provider=user_embedding.provider,
            model=user_embedding.model,
            api_key=user_embedding.api_key,
            batch_size=user_embedding.batch_size,
            normalize=user_embedding.normalize,
            cache=user_embedding.cache,
        )

        response = run_query(
            req.question,
            collection_name=req.collection_name,
            db_type=VectorDBType.QDRANT,
            top_k=req.top_k,
            retrieval_settings=req.retrieval_settings,

        )

        return {
            "question": req.question,
            "answer": response
        }
    except Exception as e:
        return {
            "error": str(e)
        }
