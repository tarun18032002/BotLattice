# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/decision_controller.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Decision Controller — decides what happens after evaluation.

Decisions:
  accept  → validation passed; proceed to output
  retry   → validation failed but retries remain; go to Prompt Refiner
  stop    → validation failed and max retries exhausted; output with caveats
"""
from ..state import AgentState, Decision
from ..utils.logging import get_logger

logger = get_logger(__name__)


def decision_controller_node(state: AgentState) -> AgentState:
    status    = state.get("validation_status", "pending")
    retry     = state.get("retry_count", 0)
    max_r     = state.get("max_retries", 2)

    if status == "passed":
        decision: Decision = "accept"
    elif retry < max_r:
        decision = "retry"
        retry += 1
    else:
        decision = "stop"

    logger.info(
        "decision_controller | status=%s retry=%d/%d → %s",
        status, retry, max_r, decision,
    )
    return {**state, "decision": decision, "retry_count": retry}
