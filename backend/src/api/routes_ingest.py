from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import shutil
import logging
import json

from src.pipeline.ingestion.pipeline import run_ingestion_pipeline
from src.logger.logging import StreamLogHandler
from src.pipeline.config.schemas import IngestRequest

router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    config: str = Form(...)
):

    config = IngestRequest.model_validate_json(config)

    async def log_stream():

        logs = []

        handler = StreamLogHandler(logs)
        logging.getLogger().addHandler(handler)

        yield json.dumps({
            "msg": "Starting ingestion...",
            "level": "info"
        }) + "\n"

        file_location = f"temp/{file.filename}"

        # Save uploaded file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        yield json.dumps({
            "msg": "File uploaded successfully",
            "level": "success"
        }) + "\n"

        # Run pipeline and stream logs
        for log in run_ingestion_pipeline(
            file_path=file_location,
            chunking=config.chunking,
            embedding=config.embedding,
            vectordb=config.vectordb
        ):
            yield log

        yield json.dumps({
            "msg": "Ingestion complete",
            "level": "success",
            "done": True
        }) + "\n"

        logging.getLogger().removeHandler(handler)

    return StreamingResponse(log_stream(), media_type="application/json")