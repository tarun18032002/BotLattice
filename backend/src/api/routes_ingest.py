from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import shutil
import logging
import json
from src.pipeline.ingestion.pipeline import run_ingestion_pipeline
from src.logger.logging import StreamLogHandler
from src.pipeline.config.vector_store import DBType


router = APIRouter()

@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    collection_name: str = Form(...)
):

    async def log_stream():

        logs = []

        handler = StreamLogHandler(logs)
        logging.getLogger().addHandler(handler)

        yield json.dumps({"msg": "Starting ingestion...", "level": "info"}) + "\n"

        file_location = f"{file.filename}"

        # with open(file_location, "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)

        yield json.dumps({"msg": "File uploaded", "level": "success"}) + "\n"

        # run pipeline
        run_ingestion_pipeline(
            file_path=file_location,
            db_type=DBType.QDRANT,
            collection_name=collection_name
        )

        # stream captured logs
        for log in logs:
            yield log

        yield json.dumps({
            "msg": "Ingestion complete",
            "level": "success",
            "done": True
        }) + "\n"

        logging.getLogger().removeHandler(handler)

    return StreamingResponse(log_stream(), media_type="application/json")