# pipeline.py
from dotenv import load_dotenv 

load_dotenv()
from pipeline.ingestion.reader import Reader
from pipeline.ingestion.chunking import Chunking
from pipeline.config.vector_store import VectorDBFactory, DBType
import pipeline.config.settings
from pipeline.query.query_pipeline import run_query

def run_ingestion_pipeline(
    file_path: str, 
    db_type: DBType, 
    collection_name: str,
    chunk_size: int = 512
):
    print(f"--- Starting Ingestion for {file_path} ---")

    # 1. Load Data
    reader = Reader(file_path)
    documents = reader.load()
    print(f"Successfully loaded {len(documents)} document(s).")

    # 2. Chunk Data
    chunker = Chunking(chunking_type="sentence", chunk_size=chunk_size)
    nodes = chunker.split(documents)
    print(f"Split documents into {len(nodes)} nodes.")

    # 3. Connect to Vector DB & Ingest
    # This step handles the embedding and storage automatically via LlamaIndex
    index = VectorDBFactory.create_index(
        db_type=db_type,
        collection_name=collection_name,
        nodes=nodes,
        dim=1536  # Adjust based on your embedding model
    )

    print(f"--- Ingestion to {db_type.value} complete! ---")
    return index

if __name__ == "__main__":
    # Example Usage:
    # Ensure your QDRANT_URL or PINECONE_API_KEY are in your environment
    # run_ingestion_pipeline(
    #     file_path="test/input/22365_3_Prompt Engineering_v7 (1).pdf",
    #     db_type=DBType.QDRANT,
    #     collection_name="prompt_guide"
    # )
    from time import time
    start_time = time()
    print(f"start time --> {start_time}")
    response = run_query(
        "what is this person education qualifincation?",
        collection_name="resume",
        db_type=DBType.QDRANT
    )
    end_time = time()
    print(f"End time --> {end_time}")
    print(f"Total execution time --> {end_time - start_time} seconds")
    print(f"response :  {response}")

