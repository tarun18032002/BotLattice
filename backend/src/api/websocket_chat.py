from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.pipeline.query.query_pipeline import run_query
from src.pipeline.config.enums import VectorDBType
import json
import asyncio

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()
    print("Client connected")

    try:
        while True:

            data = await websocket.receive_text()
            message = json.loads(data)

            question = message.get("question")
            collection = message.get("collection_name", "resume")

            # run blocking query in thread
            response = await asyncio.to_thread(
                run_query,
                question,
                collection_name=collection,
                db_type=VectorDBType.QDRANT
            )

            await websocket.send_text(json.dumps({
                "question": question,
                "answer": str(response)
            }))

    except WebSocketDisconnect:
        print("Client disconnected")