from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import shutil
import logging
import json
import os
import tempfile

from src.pipeline.config  import settings
from src.pipeline.ingestion.pipeline import run_ingestion_pipeline
from src.logger.logging import StreamLogHandler
from src.pipeline.config.schemas import ChunkingRequest,CollectionRequest


router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    chunking: str = Form(...),
    collection:str = Form(...),

):
    try:
        chunking_obj = ChunkingRequest.model_validate_json(chunking)
        collection_obj = CollectionRequest.model_validate_json(collection)
    except Exception as e:
        # It's better to catch this early before entering the StreamingResponse
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")


    async def log_stream():

        logs = []

        handler = StreamLogHandler(logs)
        logging.getLogger().addHandler(handler)

        try:
            yield json.dumps({
                "msg": "Starting ingestion...",
                "level": "info"
            }) + "\n"

            with tempfile.TemporaryDirectory() as temp_dir:
                file_location = os.path.join(temp_dir, file.filename)

                # Save uploaded file in a temporary directory that is auto-cleaned.
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                yield json.dumps({
                    "msg": "File uploaded successfully",
                    "level": "success"
                }) + "\n"

                # Run pipeline and stream logs
                for log in run_ingestion_pipeline(
                    file_path=file_location,
                    chunking=chunking_obj,
                    collection= collection_obj

                ):
                    yield log

            yield json.dumps({
                "msg": "Ingestion complete",
                "level": "success",
                "done": True
            }) + "\n"
        finally:
            logging.getLogger().removeHandler(handler)

    return StreamingResponse(log_stream(), media_type="application/json")