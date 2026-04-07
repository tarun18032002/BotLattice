# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/agents/evaluator.py
# Multi-Evaluator Layer — runs Critic then Validator in sequence
# ═══════════════════════════════════════════════════════════════════════════════
"""The evaluator runs two sub-evaluators:
  1. Critic   - qualitative review (style, clarity, completeness)
  2. Validator - strict factual / structural check (hallucinations, errors)

Both results are merged into state so the Decision Controller can act on them.
"""
from pydantic import BaseModel, Field

from ..state import AgentState, ValidationStatus
from ..config import settings
from ..utils.logging import get_logger
from ..utils.base_agent import create_custom_agent

logger = get_logger(__name__)


def _get_agent_description(state: AgentState) -> str:
    # Support both canonical and legacy key names produced by upstream nodes.
    return state.get("description", "") or state.get("Agent_description", "")


def _run_critic(state: AgentState) -> str:
    agent_description = _get_agent_description(state)

    critic_prompt = (
        "You are a critic agent. Evaluate the following prompt draft and agent description for clarity, precision, and alignment with the user's intent. Provide specific, actionable feedback on how to improve both artifacts.\n\n"
        "This content is generated for an agentic platform where a main orchestrator invokes downstream agents using the generated prompt. The prompt and description should be easy for the orchestrator to interpret, and should let the invoked agent perform tasks aligned with user intent.\n\n"
        "Here is the user intent:\n"
        + state.get("intent", "")
        + "\n\n"
        "Context Summary:\n"
        + state.get("context_summary", "")
        + "\n\n"
        "Templates provided:\n"
        + state.get("prompt_template", "")
        + "\n\n"
        "Here is the prompt draft:\n"
        + state.get("prompt_draft", "")
        + "\n\n"
        "Here is the agent description:\n"
        + agent_description
    )

    class CriticOutput(BaseModel):
        critique: list[str] = Field(
            ...,
            description="Detailed list of critique points for prompt draft and agent description, with specific improvement suggestions.",
        )

    response = create_custom_agent(
        schema=CriticOutput,
        prompt=critic_prompt,
        model_name=settings.EVALUATOR_MODEL,
        temperature=0.1,
        max_tokens=800,
    )
    try:
        return "\n".join(response.critique)
    except Exception as e:
        logger.error("evaluator | Critic failed to produce valid JSON: %s", str(e))
        return "Critic failed to produce valid feedback."


def _run_validator(
    state: AgentState,
) -> tuple[ValidationStatus, list[str], list[str]]:
    agent_description = _get_agent_description(state)

    validator_prompt = (
        "You are a strict prompt validator. Check the following prompt draft and agent description against the original user intent and context summary. "
        "Identify any factual inaccuracies, hallucinations, or misalignments with the intent."
    )

    class ValidatorOutput(BaseModel):
        status: ValidationStatus = Field(
            ..., description="Overall validation status: 'passed' or 'failed'."
        )
        errors: list[str] = Field(
            default_factory=list,
            description="List of specific errors or issues found in the prompt draft or agent description.",
        )
        hallucination_flags: list[str] = Field(
            default_factory=list,
            description="List of hallucinated information detected in the prompt draft or agent description.",
        )

    def create_validator_prompt() -> str:
        return (
            f"{validator_prompt}\n\n"
            f"User Intent:\n{state.get('intent', '')}\n\n"
            f"Context Summary:\n{state.get('context_summary', '')}\n\n"
            f"Prompt Draft:\n{state.get('prompt_draft', '')}\n\n"
            f"Agent Description:\n{agent_description}\n\n"
            f"Templates:\n{state.get('prompt_template', '')}\n"
        )

    response = create_custom_agent(
        schema=ValidatorOutput,
        prompt=create_validator_prompt(),
        model_name=settings.EVALUATOR_MODEL,
        temperature=0.0,
        max_tokens=800,
    )
    try:
        return response.status, response.errors, response.hallucination_flags
    except Exception as e:
        logger.error("evaluator | Validator failed to produce valid JSON: %s", str(e))
        return "failed", [], []


def evaluator_node(state: AgentState) -> AgentState:
    agent_description = _get_agent_description(state)
    logger.info(
        "evaluator | prompt_draft_len=%d agent_description_len=%d",
        len(state.get("prompt_draft", "")),
        len(agent_description),
    )

    critique = _run_critic(state)
    logger.debug("evaluator | critique=%s", critique[:120])

    status, errors, flags = _run_validator(state)
    logger.info("evaluator | validation_status=%s errors=%d", status, len(errors))

    return {
        "critique": critique,
        "validation_status": status,
        "validation_errors": errors,
        "hallucination_flags": flags,
    }
