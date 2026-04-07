# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/orchestrator.py
# ═══════════════════════════════════════════════════════════════════════════════
import time
from ..state import AgentState
from ..config import settings
from ..utils.logging import get_logger
from ..utils.base_agent import create_custom_agent
from ..utils.prompt import get_orchestrator_prompt
from ..utils.schema import OrchestratorOutput

logger = get_logger(__name__)


def orchestrator_node(state: AgentState) -> AgentState:
    t0 = time.perf_counter()
    user_request = state.get("user_request", "")
    logger.info("orchestrator | request=%s", user_request[:80])

    response = create_custom_agent(
        schema=OrchestratorOutput,
        max_tokens=200,
        temperature=0.2,
        model_name=settings.ORCHESTRATOR_MODEL,
        prompt=get_orchestrator_prompt(user_request),
    )

    elapsed = time.perf_counter() - t0
    meta = dict(state.get("metadata", {}))
    meta["orchestrator_ms"] = round(elapsed * 1000)

    return {
        "intent": response.intent or "",
        "error": None,
        "metadata": meta,
        "retry_count": state.get("retry_count", 0),
        "max_retries": state.get("max_retries", 2),
    }


