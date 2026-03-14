from pipeline.config.vector_store import VectorDBFactory,DBType

from pipeline.query.retriever import get_retriever
from pipeline.query.query_engine import build_query_engine

def run_query(query:str,collection_name:str,db_type:DBType):
    """
    Main RAG Query pipeline 
    """


    # Connect to existing vector store
    index = VectorDBFactory.create_index(
        db_type= db_type,
        collection_name=collection_name
    )

    # Create retriever
    retriever = get_retriever(index)

    # Create query engine
    query_engine = build_query_engine(retriever)

    # Run query
    response = query_engine.query(query)

    return response