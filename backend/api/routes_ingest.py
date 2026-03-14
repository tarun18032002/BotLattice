from fastapi import APIRouter, UploadFile, File
from pipeline.ingestion.pipeline import run_ingestion_pipeline
from pipeline.config.vector_store import DBType
import shutil

router = APIRouter()

@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    collection_name: str = "default",
    # chunking
    # vector db info
    # Embedding Model

):

    file_location = f"temp/{file.filename}"
    file_location = "tarunResume_27_10_2025.pdf"

    # with open(file_location, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)

    run_ingestion_pipeline(
        file_path=file_location,
        db_type=DBType.QDRANT,
        collection_name=collection_name
    )

    return {"status": "success", "message": "Document ingested"}