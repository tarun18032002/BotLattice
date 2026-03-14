from fastapi import APIRouter
from pydantic import BaseModel
from pipeline.query.query_pipeline import run_query
from pipeline.config.vector_store import DBType

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    collection_name: str

@router.post("/query")
def query_rag(req: QueryRequest):

    response = run_query(
        req.question,
        collection_name=req.collection_name,
        db_type=DBType.QDRANT
    )

    return {
        "question": req.question,
        "answer": response
    }