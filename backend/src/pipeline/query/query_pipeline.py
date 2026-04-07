from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.enums import VectorDBType, CollectionMode
from src.pipeline.query.retriever import get_retriever
from src.pipeline.query.query_engine import build_query_engine
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_query(query:str,collection_name:str,db_type:VectorDBType):
    """
    Main RAG Query pipeline 
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if not isinstance(collection_name, str) or not collection_name.strip():
        raise ValueError("collection_name must be a non-empty string")

    query = query.strip()
    collection_name = collection_name.strip()


    # Connect to existing vector store
    index = VectorDBFactory.create_index(
        db_type= db_type,
        mode=CollectionMode.APPEND_TO_EXISTING,
        collection_name=collection_name
    )

    # Create retriever
    retriever = get_retriever(index)

    # Create query engine
    query_engine = build_query_engine(retriever)

    # Run query
    response = query_engine.query(query)

    return response



def run_batch_queries_parallel(queries: list[str], collection_name: str, db_type: VectorDBType):
    """
    Run multiple queries in parallel
    """

    index = VectorDBFactory.create_index(
        db_type=db_type,
        mode=CollectionMode.APPEND_TO_EXISTING,
        collection_name=collection_name
    )

    retriever = get_retriever(index)
    query_engine = build_query_engine(retriever)

    def process_query(q):
        return query_engine.query(q)

    responses = [None] * len(queries)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_query, q): i for i, q in enumerate(queries)}

        for future in as_completed(futures):
            idx = futures[future]
            responses[idx] = future.result()

    return responses