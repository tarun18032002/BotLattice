# multi_agent/graph.py
#
# Pipeline:
#
#   Orchestrator
#       │
#   Confirm Intent  ← human-in-the-loop (pause for user confirmation)
#       │
#   Intent Analyzer
#       │
#   Context Builder  ← RAG + templates
#       │
#   Prompt Writer
#       │
#   Multi-Evaluator  (Critic + Validator)
#       │
#   Decision Controller  → accept / retry / stop
#       │                        │
#   [Output]          Prompt Refiner ─► Prompt Writer (loop)

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .agents.orchestrator        import orchestrator_node
from .agents.confirm_intent      import confirm_intent_node
from .agents.intent_analyzer     import intent_analyzer_node
from .agents.context_builder     import context_builder_node
from .agents.prompt_writer       import prompt_writer_node
from .agents.evaluator           import evaluator_node
from .agents.decision_controller import decision_controller_node
from .agents.prompt_refiner      import prompt_refiner_node
from .synthesizer                import synthesizer_node
from .utils.logging              import get_logger

logger = get_logger(__name__)


# ── Routing functions ────────────────────────────────────────────────────────

def route_after_orchestrator(state: AgentState) -> str:
    if state.get("error"):
        return END
    return "confirm_intent"


def route_after_confirm(state: AgentState) -> str:
    if state.get("intent_confirmed"):
        return "intent_analyzer"
    return END


def route_after_decision(state: AgentState) -> str:
    decision = state.get("decision", "accept")
    if decision == "retry":
        return "prompt_refiner"
    return "synthesizer"          # accept or stop both go to output


# ── Graph builder ────────────────────────────────────────────────────────────

def build_graph(checkpointer=None) -> StateGraph:
    g = StateGraph(AgentState)

    # ── Nodes ────────────────────────────────────────────────────────────────
    g.add_node("orchestrator",         orchestrator_node)
    # Parses & validates the raw user request; emits `intent`.

    g.add_node("confirm_intent",       confirm_intent_node)
    # Human-in-the-loop: pauses graph, surfaces rephrased intent to user.
    # Resumes with True (confirmed) or False (rejected → END).

    g.add_node("intent_analyzer",      intent_analyzer_node)
    # Performs lightweight normalization and stores `analyzed_intent`.


    g.add_node("context_builder",      context_builder_node)
    # RAG retrieval + template selection; emits `rag_context`,
    # `templates_used`, `context_summary`.

    g.add_node("prompt_writer",        prompt_writer_node)
    # Crafts the prompt from intent + context (or refines existing draft);
    # emits `prompt_draft`.

    g.add_node("evaluator",            evaluator_node)
    # Multi-Evaluator: runs Critic then Validator;
    # emits `critique`, `validation_status`, `validation_errors`,
    # `hallucination_flags`.

    g.add_node("decision_controller",  decision_controller_node)
    # Reads evaluation results and sets `decision` (accept/retry/stop).

    g.add_node("prompt_refiner",       prompt_refiner_node)
    # Optional: rewrites `prompt_draft` using evaluator feedback;
    # emits `refined_prompt`.  Then loops back to prompt_writer.

    g.add_node("synthesizer",          synthesizer_node)
    # Assembles `final_output` from `prompt_draft` + metadata.

    # ── Entry ─────────────────────────────────────────────────────────────────
    g.set_entry_point("orchestrator")

    # ── Edges ─────────────────────────────────────────────────────────────────
    g.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {"confirm_intent": "confirm_intent", END: END},
    )
    g.add_conditional_edges(
        "confirm_intent",
        route_after_confirm,
        {"intent_analyzer": "intent_analyzer", END: END},
    )

    # Linear spine
    g.add_edge("intent_analyzer", "context_builder")
    g.add_edge("context_builder", "prompt_writer")
    g.add_edge("prompt_writer", "evaluator")
    g.add_edge("evaluator", "decision_controller")

    # Decision fan-out
    g.add_conditional_edges(
        "decision_controller",
        route_after_decision,
        {"prompt_refiner": "prompt_refiner", "synthesizer": "synthesizer"},
    )

    # Refiner loops back into the writer for another pass
    g.add_edge("prompt_refiner", "prompt_writer")

    g.add_edge("synthesizer", END)

    return g.compile(checkpointer=checkpointer or MemorySaver())


# Singleton for import convenience
graph = build_graph()
