# multi_agent/state.py
from __future__ import annotations
from typing import Annotated, Any, Literal, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


# ── Enums ────────────────────────────────────────────────────────────────────

ValidationStatus = Literal["pending", "passed", "failed", "skipped"]
Decision = Literal["accept", "retry", "stop"]


# ── Core shared state ────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    # ── Input ────────────────────────────────────────────────────────────────
    user_request: str                        # Raw user input

    # ── Orchestrator ─────────────────────────────────────────────────────────
    intent: str                              # Parsed high-level intent
    analyzed_intent: str                     # Refined intent after analyzer step
    intent_confirmed: bool                   # User confirmed the rephrased intent
    error: str | None

    # ── Context Builder (RAG + templates) ────────────────────────────────────
    rag_context: List[str]                   # Retrieved documents / snippets
    prompt_template: str               # Names of templates applied
    context_summary: str                    # Condensed context for downstream

    # ── Retrieval config (provided via state) ────────────────────────────────
    collection_name: str
    db_type: str

    # ── Prompt Writer ─────────────────────────────────────────────────────────
    prompt_draft: str                        # Generated prompt draft
    description: str                         # Description of the prompt draft 
    # ── Multi-Evaluator (Critic + Validator) ──────────────────────────────────
    critique: str                            # Critic feedback
    validation_status: ValidationStatus
    validation_errors: list[str]
    hallucination_flags: list[str]

    # ── Decision Controller ───────────────────────────────────────────────────
    decision: Decision                       # accept | retry | stop

    # ── Prompt Refiner ────────────────────────────────────────────────────────
    refined_prompt: str                      # Refined prompt after feedback

    # ── Conversation history (append-only via reducer) ────────────────────────
    messages: Annotated[list, add_messages]

    # ── Final output ─────────────────────────────────────────────────────────
    final_output: str
    metadata: dict[str, Any]                 # Latency, token counts, etc.

    # ── Control flags ────────────────────────────────────────────────────────
    retry_count: int
    max_retries: int
