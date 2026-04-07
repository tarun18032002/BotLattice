# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/prompt_refiner.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Prompt Refiner (optional) — improves the prompt draft based on evaluator
feedback before looping back to the Prompt Writer.
"""
from ..utils.logging import get_logger
from ..config import settings
from ..utils.base_agent import create_custom_agent
from ..utils.prompt import get_prompt_refiner_prompt
from ..utils.schema import RefinementOutput
from ..state import AgentState

logger = get_logger(__name__)





def prompt_refiner_node(state: AgentState) -> AgentState:
    logger.info("prompt_refiner | retry_count=%d", state.get("retry_count", 0))

    errors   = state.get("validation_errors", [])
    critique = state.get("critique", "")


    response = create_custom_agent(
        schema=RefinementOutput,
        prompt=get_prompt_refiner_prompt(
            prompt_draft=state.get("prompt_draft", ""),
            critique=critique,
            validation_errors=errors,
        ),
        model_name=settings.PROMPT_REFINER_MODEL,
        temperature=0.2,
        max_tokens=1200,
    )

    try:
        return {"refined_prompt": response.refined_prompt}
    except Exception as e:
        logger.error("prompt_refiner | Refinement failed to produce valid JSON: %s", str(e))
        return {"refined_prompt": "Refinement failed to produce valid feedback."}
    
