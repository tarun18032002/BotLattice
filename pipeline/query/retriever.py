from llama_index.core.retrievers import VectorIndexRetriever


def get_retriever(index, similarity_top_k: int = 5):
    """
    Create retriever from vector index.
    """
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=similarity_top_k,
    )

    return retriever