from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import logging
import json
import os
import tempfile
from fastapi import Depends

from src.pipeline.config.embedding_config import EmbeddingConfig
from src.pipeline.config.chunking_state import ChunkingConfig
from src.pipeline.config.collection_state import CollectionConfig
from src.pipeline.ingestion.pipeline import run_ingestion_pipeline
from src.logger.logging import StreamLogHandler
from src.pipeline.config.schemas import ChunkingRequest,CollectionRequest

from src.database.models import AuthUser
from src.api.routes_auth import get_current_auth_user


router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    chunking: str = Form(...),
    collection: str = Form(...),
    current_user: AuthUser = Depends(get_current_auth_user)

):
    incoming_chunking = None
    incoming_collection = None

    try:
        incoming_chunking = ChunkingRequest.model_validate_json(chunking)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid chunking JSON data: {str(e)}")

    try:
        incoming_collection = CollectionRequest.model_validate_json(collection)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid collection JSON data: {str(e)}")

    # Source of truth is DB. If config rows are missing, allow one-time bootstrap
    # from incoming payload and persist those values.
    if not ChunkingConfig.exists(user_id=current_user.id):
        if incoming_chunking is None:
            raise HTTPException(
                status_code=400,
                detail="No chunking config found in DB. Save chunking config first.",
            )
        ChunkingConfig.from_request(incoming_chunking).save(user_id=current_user.id)

    if not CollectionConfig.exists(user_id=current_user.id):
        if incoming_collection is None:
            raise HTTPException(
                status_code=400,
                detail="No collection config found in DB. Save collection config first.",
            )
        CollectionConfig.from_request(incoming_collection).save(user_id=current_user.id)

    chunking_obj = ChunkingConfig.load(user_id=current_user.id).to_request()
    collection_obj = CollectionConfig.load(user_id=current_user.id).to_request()


    async def log_stream():

        logs = []
        chunk_count = 0
        doc_count = 0

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

                embedding_state = EmbeddingConfig.load(user_id=current_user.id)
                if not embedding_state.connected or embedding_state.dimension <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail="No valid embedding config found for this user. Connect embeddings first."
                    )

                # Run pipeline and stream logs
                for log in run_ingestion_pipeline(
                    file_path=file_location,
                    chunking=chunking_obj,
                    collection= collection_obj,
                    dim = embedding_state.dimension 

                ):
                    yield log
                    # Capture metadata from pipeline
                    try:
                        parsed = json.loads(log.strip())
                        if "chunks" in parsed and isinstance(parsed["chunks"], int):
                            chunk_count = parsed["chunks"]
                        if "documents" in parsed and isinstance(parsed["documents"], int):
                            doc_count = parsed["documents"]
                    except (json.JSONDecodeError, AttributeError):
                        pass

            yield json.dumps({
                "msg": "Ingestion complete",
                "level": "success",
                "done": True,
                "chunks": chunk_count,
                "documents": doc_count
            }) + "\n"
        finally:
            logging.getLogger().removeHandler(handler)

    return StreamingResponse(log_stream(), media_type="application/x-ndjson")