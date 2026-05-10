import json

from src.pipeline.ingestion.reader import Reader
from src.pipeline.ingestion.chunking import Chunking
from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.schemas import ChunkingRequest,CollectionRequest
from src.pipeline.config.settings import vectordb


def run_ingestion_pipeline(
    file_path: str,
    chunking: ChunkingRequest,
    collection: CollectionRequest
):
    try :
        yield json.dumps({
            "msg": f"--- Starting Ingestion for {file_path} ---",
            "level": "info"
        }) + "\n"
        print(f"--- Starting Ingestion for {file_path} ---")

        # 1️⃣ Load Data
        reader = Reader(file_path)
        documents = reader.load()
        
        doc_count = len(documents)

        yield json.dumps({
            "msg": f"Successfully loaded {doc_count} document(s)",
            "level": "info"
        }) + "\n"
        
        # Send document count as metadata for UI stats
        yield json.dumps({
            "msg": f"Documents loaded: {doc_count}",
            "level": "info",
            "documents": doc_count
        }) + "\n"
        print(f"Successfully loaded {doc_count} document(s).")

        # 2️⃣ Chunk Data
        chunker = Chunking(chunking_request=chunking)
        nodes = chunker.split(documents)
        
        chunk_count = len(nodes)

        yield json.dumps({
            "msg": f"Split documents into {chunk_count} nodes",
            "level": "info"
        }) + "\n"
        
        # Send chunk count as metadata for UI stats
        yield json.dumps({
            "msg": f"Chunks created: {chunk_count}",
            "level": "info",
            "chunks": chunk_count
        }) + "\n"
        print(f"Split documents into {chunk_count} nodes.")

        # 3️⃣ Vector DB ingestion
        db_type = vectordb.vectordb_type

        yield json.dumps({
            "msg": f"Connecting to Vector DB: {db_type}",
            "level": "info"
        }) + "\n"

        index = None
        index_stream = VectorDBFactory.create_index_with_logs(
            db_type=db_type,
            collection_name=collection.collection_name,
            mode=collection.mode,
            nodes=nodes,
            dim=1536
        )
        try:
            while True:
                yield next(index_stream)
        except StopIteration as stop:
            index = stop.value
    
        yield json.dumps({
            "msg": f"Ingestion to {db_type} completed successfully",
            "level": "success"
        }) + "\n"
        print(f"--- Ingestion to {db_type} complete! ---")

        return index
    except Exception as e:
        yield json.dumps({
            "msg": f"Error during ingestion: {str(e)}",
            "level": "error"
        }) + "\n"
        