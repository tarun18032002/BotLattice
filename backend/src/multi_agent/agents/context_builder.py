# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/context_builder.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Context Builder - retrieves RAG context and applies prompt templates.

Flow:
  1. Query the vector store with the analyzed intent (RAG retrieval).
  2. Select relevant prompt templates based on intent keywords.
  3. Summarise everything into `context_summary` for the Prompt Writer.
"""
from ...pipeline.config.enums import VectorDBType
from ..state import AgentState
from ..utils.logging import get_logger
from ..utils.base_agent import create_custom_agent
from ..utils.prompt import get_RAG_Query_Generator_Prompt, get_context_builder_prompt
from ..utils.schema import QueryTemplateOutput, ContextBuilderOutput
from ...pipeline.query.query_pipeline import run_batch_queries_parallel



logger = get_logger(__name__)



def query_generator_agent(intent: str) -> list[str]:
    """Generate retrieval queries from intent."""
    response = create_custom_agent(
        schema=QueryTemplateOutput,
        prompt=get_RAG_Query_Generator_Prompt(intent),
    )
    return response.queries

    

def context_builder_node(state: AgentState) -> AgentState:
    analyzed = state.get("analyzed_intent", state.get("intent", ""))
    logger.info("context_builder | analyzed_intent=%s", analyzed[:80])

    collection_name = state.get("collection_name", "resume")
    db_type_str = state.get("db_type", VectorDBType.QDRANT.value)
    try:
        db_type = VectorDBType(db_type_str)
    except ValueError:
        logger.warning("context_builder | invalid db_type=%s, fallback=qdrant", db_type_str)
        db_type = VectorDBType.QDRANT

    queries = query_generator_agent(intent=analyzed)

    try:
        rag_context = run_batch_queries_parallel(
            queries=queries,
            collection_name=collection_name,
            db_type=db_type,
        )
    except Exception as e:
        logger.warning("context_builder | retrieval failed, continuing without RAG context: %s", str(e))
        rag_context = []

    if not rag_context:
        logger.warning("context_builder | no RAG context retrieved for intent: %s", analyzed)
        rag_context = []

    rag_context_text = [str(item) for item in rag_context]
    response = create_custom_agent(
        schema=ContextBuilderOutput,
        prompt=get_context_builder_prompt(intent=analyzed, context=rag_context_text),
    )

    return {
        "prompt_template": response.prompt_template,
        "context_summary": response.context_summary,
        "rag_context": rag_context_text,
    }
    