from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Type



from ..utils.logging import get_logger


logger = get_logger(__name__)


def create_custom_agent(schema: Type[BaseModel], prompt: str, model_name: str = 'gpt-5.4-nano', temperature: float = 0, max_tokens: int = 400):
    model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30
        )

    agent = create_agent(
        model=model,
        response_format=schema
    )

    resp = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    try:
        return resp["structured_response"]
    except Exception as e:
        logger.error("Error while parsing structured response: %s", str(e))
        return None



