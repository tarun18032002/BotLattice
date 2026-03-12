import os
from llama_index.core import Settings
from llama_index.llms.google_genai import GoogleGenAI
# from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# 1. Setup API Key and Base URL
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')



# 2. Configure Grok LLM
# Common models: "grok-2-latest", "grok-beta", "grok-3"
Settings.llm = GoogleGenAI(
    model="gemini-2.5-flash",
    # api_key="some key",  # uses GOOGLE_API_KEY env var by default
)

# 3. Configure Grok Embedding Model
# Note: Check xAI docs for the specific embedding model name (e.g., "grok-embed")
# Settings.embed_model = GoogleGenAIEmbedding(
#     model_name="gemini-embedding-2-preview",
#     embed_batch_size=100,
#     # can pass in the api key directly
#     # api_key="...",
#     # or pass in a vertexai_config
#     # vertexai_config={
#     #     "project": "...",
#     #     "location": "...",
#     # }
#     # can also pass in an embedding_config
#     # embedding_config=EmbedContentConfig(...)
# )


Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")