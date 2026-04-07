# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/intent_analyzer.py
# ═══════════════════════════════════════════════════════════════════════════════
"""Intent analyzer node.

Currently this performs light normalization and preserves the original intent.
The node exists so downstream steps can rely on `analyzed_intent` being present
in state.
"""

from ..state import AgentState
from ..utils.logging import get_logger

logger = get_logger(__name__)


def intent_analyzer_node(state: AgentState) -> AgentState:
    raw_intent = state.get("intent", "")
    analyzed_intent = " ".join(raw_intent.split())
    logger.info("intent_analyzer | intent_len=%d", len(analyzed_intent))
    return {"analyzed_intent": analyzed_intent}
