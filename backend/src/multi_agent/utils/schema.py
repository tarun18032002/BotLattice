from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class OrchestratorOutput(BaseModel):
    intent: Optional[str] = Field(None, description="The distilled intent from the user request.")
    validation_errors: Optional[List[str]] = Field(None, description="List of validation errors if the request is invalid.")


class QueryTemplateOutput(BaseModel):
    queries: List[str] = Field(..., description="List of queries generated for RAG retrieval based on the intent.", max_items=5)

class ContextBuilderOutput(BaseModel):
    prompt_template: str = Field(..., description= "The prompt template selected based on the analyzed intent and retrieved RAG context. This should be one of the predefined templates in the system.")
    context_summary: str = Field(..., description="A concise synthesis of the retrieved RAG context and any applicable templates. This summary should provide relevant information that can be used by the Prompt Writer to craft an effective prompt.")


class PromptWriterOutput(BaseModel):
    prompt_draft: str = Field(
        ...,
        description=(
            "A well-structured system prompt designed to guide an LLM in accomplishing the user's intent. "
            "It should be clear, specific, and actionable, leveraging the provided context and templates where relevant."
        ),
    )
    
    description: str = Field(
        ...,
        description=(
            "A concise summary of the agent’s role and purpose. "
            "It should explain what the agent does and how it aligns with the user’s intent, "
            "helping the orchestrator determine when to use this agent."
        ),
    )


class RefinementOutput(BaseModel):
    refined_prompt: str = Field(..., description="An improved version of the prompt draft that addresses the critique and validation errors provided by the evaluator. The refined prompt should be more likely to pass validation and effectively guide the LLM in fulfilling the user's intent.")