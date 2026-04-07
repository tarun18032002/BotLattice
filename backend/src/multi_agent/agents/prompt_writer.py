# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/prompt_writer.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Prompt Writer — crafts the best possible prompt using intent + context.

On a retry loop it receives `refined_prompt` from the Prompt Refiner and uses
that as its starting point instead of building from scratch.
"""
from ..state import AgentState
from ..config import settings
from ..utils.logging import get_logger
from ..utils.base_agent import create_custom_agent
from ..utils.prompt import get_prompt_writer_prompt
from ..utils.schema import PromptWriterOutput


logger = get_logger(__name__)


def prompt_writer_node(state: AgentState) -> AgentState:
    logger.info("prompt_writer | retry_count=%d", state.get("retry_count", 0))

    base_draft = state.get("refined_prompt", "")
    writer_prompt = get_prompt_writer_prompt(
        intent=state.get("intent", ""),
        context_summary=state.get("context_summary", ""),
        templates=state.get("prompt_template", ""),
    )
    if base_draft:
        writer_prompt += "\n\nRefined Draft (start from this):\n" + base_draft

    response = create_custom_agent(
        schema=PromptWriterOutput,
        prompt=writer_prompt,
        model_name=settings.PROMPT_WRITER_MODEL,
        temperature=0.2,
        max_tokens=1200,
    )

    if not response.prompt_draft:
        logger.error("prompt_writer | failed to generate prompt draft")
        return {"error": "Failed to generate prompt draft"}

    logger.debug("prompt_writer | draft_len=%d description_len=%d", len(response.prompt_draft), len(response.description))
    return {"prompt_draft": response.prompt_draft, "description": response.description}
