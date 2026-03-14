from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer


from .prompt import qa_prompt

def build_query_engine(retriever):
    """
        Build query engine with custom prompt.
    """

    response_synthesizer = get_response_synthesizer(
        text_qa_template=qa_prompt
    )

    query_engine = RetrieverQueryEngine(
        retriever = retriever,
        response_synthesizer=response_synthesizer
    )

    return query_engine