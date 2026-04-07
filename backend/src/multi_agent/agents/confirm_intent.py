# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/confirm_intent.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Human-in-the-loop node that pauses the graph to let the user confirm
or reject the rephrased intent produced by the Orchestrator.

Usage (caller side):
    # Run the graph — it will pause at confirm_intent
    result = graph.invoke({"user_request": "..."}, config)

    # The interrupt surfaces: {"intent": "...", "message": "..."}
    # User reviews and resumes:
    from langgraph.types import Command
    result = graph.invoke(Command(resume=True), config)   # confirmed
    result = graph.invoke(Command(resume=False), config)  # rejected → END
"""
from langgraph.types import interrupt
from ..state import AgentState
from ..utils.logging import get_logger

logger = get_logger(__name__)


def confirm_intent_node(state: AgentState) -> AgentState:
    intent = state.get("intent", "")
    logger.info("confirm_intent | awaiting user confirmation for: %s", intent[:80])

    # Pause execution and surface the intent to the caller / UI
    confirmed = interrupt({
        "intent": intent,
        "message": "Is this rephrased intent correct?",
    })

    logger.info("confirm_intent | user responded: %s", confirmed)
    return {"intent_confirmed": bool(confirmed)}
