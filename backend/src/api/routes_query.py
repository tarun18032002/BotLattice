from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.pipeline.query.query_pipeline import run_query
from src.pipeline.config.enums import VectorDBType

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    collection_name: str
    top_k: Optional[int] = None
    retrieval_settings: Optional[dict] = None

@router.post("/query")
def query_rag(req: QueryRequest):
    try : 
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
