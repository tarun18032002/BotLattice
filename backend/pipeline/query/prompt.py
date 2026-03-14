from llama_index.core.prompts import PromptTemplate

QA_PROMPT_TEMPLATE = """
You are an assistant answering questions based on provided context.

Context:
{context_str}

Question:
{query_str}

Answer clearly and concisely.
"""

qa_prompt = PromptTemplate(QA_PROMPT_TEMPLATE)