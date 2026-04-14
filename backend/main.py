from dotenv import load_dotenv 

load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.logger import logging
from src.api.routes_ingest import router as ingest_router
from src.api.routes_query import router as query_router
from src.api.websocket_chat import router as ws_router
from src.api.routes_chunking import router as chunking_router
from src.api.routes_vectordb import router as vectordb_router
from src.api.routes_embeddings import router as embeddings_router

from fastapi.middleware.cors import CORSMiddleware
import src.pipeline.config.settings


def _restore_embed_model():
    """Re-instantiate Settings.embed_model from persisted config on startup."""
    from src.pipeline.config.embedding_config import active_embedding
    from src.pipeline.config.embedding_factory import create_embed_model
    from llama_index.core import Settings

    if not active_embedding.connected:
        return

    try:
        provider = active_embedding.provider
        model    = active_embedding.model
        api_key  = active_embedding.api_key

        Settings.embed_model = create_embed_model(
            provider=provider,
            model=model,
            api_key=api_key,
            batch_size=active_embedding.batch_size,
            normalize=active_embedding.normalize,
            cache=active_embedding.cache,
        )

        print(f"[startup] Restored embed model: {provider}/{model}")
    except Exception as exc:
        print(f"[startup] Could not restore embed model: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _restore_embed_model()
    yield


app = FastAPI(title="RAG Chatbot API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(ws_router)
app.include_router(chunking_router)
app.include_router(vectordb_router)
app.include_router(embeddings_router)
