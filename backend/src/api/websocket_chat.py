from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.pipeline.query.query_pipeline import run_query
from src.pipeline.config.enums import VectorDBType
from src.multi_agent.graph import graph as prompt_builder_graph
from langgraph.types import Command
import json
import asyncio
import uuid


router = APIRouter()

# Fields surfaced to the UI per node
_NODE_FIELDS: dict[str, list[str]] = {
    "orchestrator":        ["intent", "error"],
    "intent_analyzer":     ["analyzed_intent"],
    "context_builder":     ["context_summary"],
    "prompt_writer":       ["prompt_draft", "description"],
    "evaluator":           ["critique", "validation_status", "validation_errors", "hallucination_flags"],
    "decision_controller": ["decision"],
    "prompt_refiner":      ["refined_prompt"],
    "synthesizer":         ["final_output", "description", "metadata"],
}


def _pick(node: str, output: dict) -> dict:
    """Return only the UI-relevant fields from a node's output."""
    fields = _NODE_FIELDS.get(node, list(output.keys()))
    return {k: v for k, v in output.items() if k in fields and v is not None}


async def _run_prompt_builder(websocket: WebSocket, message: dict) -> None:
    """Stream the prompt-builder multi-agent graph over the WebSocket.

    Message protocol (server → client):
      {"type": "session_start",  "thread_id": "..."}
      {"type": "agent_update",   "node": "<name>", "data": {...}}
      {"type": "confirm_intent", "thread_id": "...", "intent": "...", "message": "..."}
      {"type": "done"}

    Message protocol (client → server, only after confirm_intent):
      {"type": "confirm", "confirmed": true|false}
    """
    thread_id = message.get("thread_id") or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "user_request":   message.get("question", ""),
        "collection_name": message.get("collection_name", "resume"),
        "db_type":        "qdrant",
        "max_retries":    3,
        "retry_count":    0,
    }

    try:
        await websocket.send_text(json.dumps({
            "type":      "session_start",
            "thread_id": thread_id,
        }))

        input_payload = initial_state  # first call uses full state; resumes use Command

        while True:
            interrupted = False

            try:
                async for chunk in prompt_builder_graph.astream(
                    input_payload, config, stream_mode="updates"
                ):
                    for node_name, node_output in chunk.items():
                        if node_name == "__interrupt__":
                            # node_output is a tuple of Interrupt objects
                            interrupt_obj = node_output[0]
                            value = (
                                interrupt_obj.value
                                if hasattr(interrupt_obj, "value")
                                else interrupt_obj
                            )
                            await websocket.send_text(json.dumps({
                                "type":      "confirm_intent",
                                "thread_id": thread_id,
                                "intent":    value.get("intent", ""),
                                "message":   value.get("message", ""),
                            }))
                            interrupted = True
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "agent_update",
                                "node": node_name,
                                "data": _pick(node_name, node_output),
                            }))
            except Exception as exc:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"Graph processing error: {str(exc)}",
                }))
                break

            if not interrupted:
                await websocket.send_text(json.dumps({"type": "done"}))
                break

            # Wait for the client's confirm/reject before resuming the graph
            try:
                raw = await websocket.receive_text()
                confirm_msg = json.loads(raw)
                confirmed = bool(confirm_msg.get("confirmed", False))
                input_payload = Command(resume=confirmed)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid JSON in confirmation message",
                }))
                break
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected during prompt_builder (thread: {thread_id})")
    except Exception as exc:
        print(f"[WS] Unexpected error in prompt_builder: {str(exc)}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"Unexpected error: {str(exc)}",
            }))
        except:
            pass


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                print(f"Received message: {message}")
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid JSON payload",
                }))
                continue

            if not isinstance(message, dict):
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid message format",
                }))
                continue

            if message.get("agent") == "prompt_builder":
                await _run_prompt_builder(websocket, message)
                continue

            # Confirm/reject payloads are only valid while inside prompt-builder
            # interrupt flow. Ignore safely if received at top level.
            if message.get("type") == "confirm":
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "No pending confirmation request",
                }))
                continue

            # ── default: RAG query ──────────────────────────────────────────
            question = message.get("question")
            if not isinstance(question, str) or not question.strip():
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Question is required",
                }))
                continue

            question = question.strip()
            collection = message.get("collection_name", "resume")
            if not isinstance(collection, str) or not collection.strip():
                collection = "resume"
            print(f"Running RAG query: '{question}' against collection '{collection}'")
            try:
                response = await asyncio.to_thread(
                    run_query,
                    query=question,
                    collection_name=collection,
                    db_type=VectorDBType.QDRANT,
                )

            except Exception as exc:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(exc),
                }))
                continue

            await websocket.send_text(json.dumps({
                "type": "rag_response",
                "query": question,
                "answer":   str(response),
            }))
            await websocket.send_text(json.dumps({"type": "done"}))

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
        return "[WS] Client disconnected"
    except Exception as exc:
        print(f"[WS] Unexpected error in main handler: {str(exc)}")
        return f"[WS] Unexpected error: {str(exc)}"