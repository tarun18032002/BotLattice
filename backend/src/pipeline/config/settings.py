import os
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
# from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
# from llama_index.embeddings.fastembed import FastEmbedEmbedding

# 1. Setup API Key and Base URL
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')



# 2. Configure Grok LLM
# Common models: "grok-2-latest", "grok-beta", "grok-3"
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)




# Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")


from src.pipeline.config.schemas import VectorDBRequest,VectorDBType
from src.pipeline.config.vectordb_state import active_vectordb

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


#  deminition for embedding model and dimension should be added here when we add support for multiple embedding models
demension = 768