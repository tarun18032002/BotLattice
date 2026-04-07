# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/synthesizer.py  —  Output node
# ═══════════════════════════════════════════════════════════════════════════════
"""Assembles the final output from the best available prompt draft.

On `accept`  → returns the prompt draft as-is (clean output).
On `stop`    → returns the draft with a Caveats section noting issues.
"""
import time
from .state import AgentState
from .utils.logging import get_logger

logger = get_logger(__name__)


def synthesizer_node(state: AgentState) -> AgentState:
    t0 = time.perf_counter()
    decision = state.get("decision", "accept")
    draft = state.get("refined_prompt") or state.get("prompt_draft", "")
    description = state.get("description", "") or state.get("Agent_description", "")
    errors   = state.get("validation_errors", [])
    flags    = state.get("hallucination_flags", [])

    logger.info(
        "synthesizer | decision=%s draft_len=%d description_len=%d",
        decision,
        len(draft),
        len(description),
    )

    if decision == "stop" and (errors or flags):
        caveats = "\n\n---\n**Caveats (max retries reached):**\n"
        if errors:
            caveats += "\n".join(f"- {e}" for e in errors) + "\n"
        if flags:
            caveats += "Hallucination flags: " + ", ".join(flags)
        final_output = draft + caveats
    else:
        final_output = draft

    meta = dict(state.get("metadata", {}))
    meta["synthesizer_ms"] = round((time.perf_counter() - t0) * 1000)

    return {"final_output": final_output, "description": description, "metadata": meta}
