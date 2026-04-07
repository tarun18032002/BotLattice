# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/config.py
# ═══════════════════════════════════════════════════════════════════════════════
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY:       str = ""
    LANGCHAIN_API_KEY:    str = ""   # optional: LangSmith tracing
    LANGCHAIN_TRACING_V2: bool = False

    # Model overrides per agent (tune cost vs quality)
    ORCHESTRATOR_MODEL:       str = "gpt-4o"
    INTENT_ANALYZER_MODEL:    str = "gpt-4o"
    CONTEXT_BUILDER_MODEL:    str = "gpt-4o-mini"
    PROMPT_WRITER_MODEL:      str = "gpt-4o-mini"
    EVALUATOR_MODEL:          str = "gpt-4o"
    DECISION_CONTROLLER_MODEL: str = "gpt-4o"
    PROMPT_REFINER_MODEL:     str = "gpt-4o-mini"
    DEFAULT_MODEL:            str = "gpt-4o-mini"

    LOG_LEVEL: str = "INFO"


settings = Settings()
