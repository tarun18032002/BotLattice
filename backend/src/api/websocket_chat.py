from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.pipeline.query.query_pipeline import run_query, run_direct_query
from src.pipeline.config.enums import VectorDBType
from src.multi_agent.graph import graph as prompt_builder_graph
from langgraph.types import Command
from src.api.routes_auth import _get_bearer_token, validate_session
from src.database.db import SessionLocal
from src.database.models import AuthUser
from src.pipeline.config.embedding_config import EmbeddingConfig
from src.pipeline.config.embedding_factory import create_embed_model
from llama_index.core import Settings
from datetime import datetime, timezone
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
    # Extract and validate authentication token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    # Validate session and get authenticated user
    db = SessionLocal()
    try:
        # Manually validate the session (can't use Depends in WebSocket)
        try:
            # Check cache first
            from src.api.routes_auth import session_cache
            if token in session_cache:
                current_user = session_cache[token]
            else:
                # Fetch session and user in a single query
                from src.database.models import AuthSession, AuthUser
                result = (
                    db.query(AuthSession, AuthUser)
                    .join(AuthUser, AuthSession.user_id == AuthUser.id)
                    .filter(AuthSession.token == token)
                    .first()
                )

                if not result:
                    await websocket.close(code=4001, reason="Invalid session token")
                    return

                session, user = result
                now = datetime.now(timezone.utc)
                expires_at = session.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)

                if expires_at < now:
                    db.delete(session)
                    db.commit()
                    await websocket.close(code=4001, reason="Session expired")
                    return

                if not user:
                    await websocket.close(code=4001, reason="User not found")
                    return

                current_user = user
                # Cache the session
                session_cache[token] = user

        except Exception as e:
            print(f"[WS] Session validation error: {str(e)}")
            await websocket.close(code=4001, reason=f"Authentication failed: {str(e)}")
            return

        # Accept the WebSocket connection after successful authentication
        await websocket.accept()
        print(f"[WS] Client authenticated: user {current_user.id}")

        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    print(f"Received message from user {current_user.id}: {message}")
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

                # if message.get("agent") == "prompt_builder":
                #     await _run_prompt_builder(websocket, message)
                #     continue

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
                top_k = message.get("top_k")
                mode = message.get("mode", "rag")
                system_prompt = message.get("system_prompt")

                # Use authenticated user's ID from the session, not from the message
                user_id = current_user.id

                if not isinstance(system_prompt, str):
                    system_prompt = None
                if not isinstance(collection, str) or not collection.strip():
                    collection = "resume"

                # Always fetch db_type from user's vector DB state (never from embedding config)
                from src.pipeline.config.vectordb_state import ensure_active_vectordb_loaded
                vectordb_state = ensure_active_vectordb_loaded(user_id=user_id)
                db_type = vectordb_state.vectordb_type or "qdrant"

                print(f"Running query for user {user_id}: mode='{mode}' question='{question}' collection='{collection}'")
                try:
                    # Load user-specific embedding configuration from database
                    user_embedding = EmbeddingConfig.load(user_id=user_id)
                    if not user_embedding.connected:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "error": "No embedding model connected for this user",
                        }))
                        continue

                    # Configure settings with user-specific embedding model
                    Settings.embed_model = create_embed_model(
                        provider=user_embedding.provider,
                        model=user_embedding.model,
                        api_key=user_embedding.api_key,
                        batch_size=user_embedding.batch_size,
                        normalize=user_embedding.normalize,
                        cache=user_embedding.cache,
                    )

                    if mode == "direct":
                        response = await asyncio.to_thread(
                            run_direct_query,
                            query=question,
                            system_prompt=system_prompt,
                            user_id=user_id,
                        )
                    else:
                        response = await asyncio.to_thread(
                            run_query,
                            query=question,
                            collection_name=collection,
                            db_type=db_type,
                            top_k=top_k,  # Only top_k is allowed as override
                            engine_settings_overrides=None,  # No client overrides for settings
                            user_id=user_id
                        )

                except Exception as exc:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": str(exc),
                    }))
                    continue

                await websocket.send_text(json.dumps({
                    "type": "direct_response" if mode == "direct" else "rag_response",
                    "query": question,
                    "answer":   str(response),
                }))
                await websocket.send_text(json.dumps({"type": "done"}))

        except WebSocketDisconnect:
            print(f"[WS] Client disconnected for user {current_user.id}")
        except Exception as exc:
            print(f"[WS] Unexpected error for user {current_user.id}: {str(exc)}")
            try:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"Unexpected error: {str(exc)}",
                }))
            except:
                pass
    finally:
        db.close()