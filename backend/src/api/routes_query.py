from fastapi import APIRouter
from pydantic import BaseModel
from src.pipeline.query.query_pipeline import run_query
from src.pipeline.config.enums import VectorDBType

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    collection_name: str

@router.post("/query")
def query_rag(req: QueryRequest):
    try : 
        response = run_query(
            req.question,
            collection_name=req.collection_name,
            db_type=VectorDBType.QDRANT,

        )

        return {
            "question": req.question,
            "answer": response
        }
    except Exception as e:
        return {
            "error": str(e)
        }
