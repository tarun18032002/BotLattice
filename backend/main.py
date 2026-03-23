from dotenv import load_dotenv 

load_dotenv()
from fastapi import FastAPI
from src.logger import logging
from src.api.routes_ingest import router as ingest_router
from src.api.routes_query import router as query_router
from src.api.websocket_chat import router as ws_router
from src.api.routes_chunking import router as chunking_router
from src.api.routes_vectordb import router as vectordb_router

from fastapi.middleware.cors import CORSMiddleware
import src.pipeline.config.settings


app = FastAPI(title="RAG Chatbot API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(ws_router)
app.include_router(chunking_router)
app.include_router(vectordb_router)
