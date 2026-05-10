import os
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
# from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
# from llama_index.embeddings.fastembed import FastEmbedEmbedding

# 1. Setup API Key and Base URL
_google_api_key = os.getenv('GOOGLE_API_KEY')
if _google_api_key:
    os.environ["GOOGLE_API_KEY"] = _google_api_key



# 2. Configure Grok LLM
# Common models: "grok-2-latest", "grok-beta", "grok-3"
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)




# Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")


from src.pipeline.config.schemas import VectorDBRequest,VectorDBType
from src.pipeline.config.vectordb_state import active_vectordb
from src.pipeline.config.embedding_config import active_embedding

_saved_db_type = active_vectordb.vectordb_type if active_vectordb.connected else VectorDBType.QDRANT.value
try:
    _db_type = VectorDBType(_saved_db_type)
except Exception:
    _db_type = VectorDBType.QDRANT

vectordb = VectorDBRequest(
    vectordb_type=_db_type,
    url=active_vectordb.url or "http://localhost:6333",
    api_key=active_vectordb.api_key,
)


# Get embedding dimension from active_embedding config, fallback to 384 (BAAI/bge-small-en-v1.5 default)
demension = active_embedding.dimension if active_embedding.dimension > 0 else 384