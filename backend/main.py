from dotenv import load_dotenv 

load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from src.logger import logging
from src.api.routes_ingest import router as ingest_router
from src.api.routes_query import router as query_router
from src.api.websocket_chat import router as ws_router
from src.api.routes_chunking import router as chunking_router
from src.api.routes_vectordb import router as vectordb_router
from src.api.routes_embeddings import router as embeddings_router
from src.api.routes_settings import router as settings_router
from src.api.routes_auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware
import src.pipeline.config.settings
from src.pipeline.config.embedding_runtime import warm_embed_model_in_background


@asynccontextmanager
async def lifespan(app: FastAPI):
    warm_embed_model_in_background()
    yield


app = FastAPI(title="RAG Chatbot API", lifespan=lifespan)

# Configure CORS origins from environment or use local defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,*").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(ingest_router)
app.include_router(settings_router)
app.include_router(chunking_router)
app.include_router(vectordb_router)
app.include_router(embeddings_router)
app.include_router(auth_router)
app.include_router(query_router)
app.include_router(ws_router)
