from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.enums import VectorDBType, CollectionMode
from src.pipeline.query.retriever import get_retriever
from src.pipeline.query.query_engine import build_query_engine
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.pipeline.config.llm_settings_state import active_llm_settings
from src.pipeline.config.embedding_runtime import ensure_embed_model_ready
from llama_index.core import Settings


def _resolve_top_k(top_k, retrieval_settings):
    saved_settings = active_llm_settings.to_dict()
    runtime_settings = retrieval_settings if isinstance(retrieval_settings, dict) else {}
    merged_settings = {**saved_settings, **runtime_settings}

    value = top_k if top_k is not None else merged_settings.get("defaultTopK", 5)
    try:
        return max(1, min(20, int(value)))
    except Exception:
        return 5

def run_query(query:str,collection_name:str,db_type:VectorDBType, top_k=None, retrieval_settings=None):
    """
    Main RAG Query pipeline 
    """
    try : 
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        if not isinstance(collection_name, str) or not collection_name.strip():
            raise ValueError("collection_name must be a non-empty string")

        query = query.strip()
        collection_name = collection_name.strip()

        # Ensure embed model is available even if startup warm-up is still running.
        ensure_embed_model_ready()

        print(f"Running RAG query: '{query}' against collection '{collection_name}' using DB '{db_type}'")
        
        # Get embedding dimension from collection metadata (stored when collection was created)
        embed_dim = VectorDBFactory.get_collection_dimension(db_type, collection_name)
        
        # Connect to existing vector store
        index = VectorDBFactory.create_index(
            db_type= db_type,
            mode=None,
            collection_name=collection_name,
            dim=embed_dim 
        )

        print(f"index of type {type(index)} created successfully for collection '{collection_name}'")
        effective_top_k = _resolve_top_k(top_k, retrieval_settings)
        # Create retriever
        retriever = get_retriever(index, similarity_top_k=effective_top_k)

        # Create query engine
        query_engine = build_query_engine(
            retriever,
            retrieval_settings=retrieval_settings,
            top_k=effective_top_k,
        )

        # Run query
        response = query_engine.query(query)

        return response
    except Exception as e:
        raise RuntimeError(f"Error during query execution: {str(e)}")


def run_direct_query(query: str, system_prompt: str | None = None):
    """Run a direct (non-RAG) LLM completion."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        saved = active_llm_settings.to_dict()
        provider = str(saved.get("llmProvider", "")).strip().lower()
        model = saved.get("llmModel") or "gpt-4o-mini"
        api_key = saved.get("apiKey")
        temperature = saved.get("temperature", 0.2)
        max_tokens = saved.get("maxTokens", 1024)

        final_system_prompt = system_prompt if isinstance(system_prompt, str) and system_prompt.strip() else saved.get("systemPrompt")

        # Prefer provider-specific OpenAI path so Direct mode follows Settings.
        if provider == "openai":
            if not isinstance(api_key, str) or not api_key.strip():
                raise RuntimeError("OpenAI API key is missing in settings")

            from openai import OpenAI

            client = OpenAI(api_key=api_key.strip())
            messages = []
            if isinstance(final_system_prompt, str) and final_system_prompt.strip():
                messages.append({"role": "system", "content": final_system_prompt.strip()})
            messages.append({"role": "user", "content": query.strip()})

            result = client.chat.completions.create(
                model=str(model),
                messages=messages,
                temperature=float(temperature),
                max_tokens=int(max_tokens),
            )

            choice = result.choices[0] if result.choices else None
            message = getattr(choice, "message", None) if choice is not None else None
            content = getattr(message, "content", None) if message is not None else None
            if isinstance(content, str) and content.strip():
                return content
            raise RuntimeError("OpenAI returned an empty response")

        llm = Settings.llm
        if llm is None:
            raise RuntimeError("No LLM configured in Settings.llm")

        prompt = query.strip()
        if isinstance(final_system_prompt, str) and final_system_prompt.strip():
            prompt = f"{final_system_prompt.strip()}\n\nUser: {query.strip()}\nAssistant:"

        if hasattr(llm, "complete"):
            result = llm.complete(prompt)
            text = getattr(result, "text", None)
            return text if isinstance(text, str) and text.strip() else str(result)

        if hasattr(llm, "chat"):
            from llama_index.core.base.llms.types import ChatMessage

            messages = []
            if isinstance(final_system_prompt, str) and final_system_prompt.strip():
                messages.append(ChatMessage(role="system", content=final_system_prompt.strip()))
            messages.append(ChatMessage(role="user", content=query.strip()))

            result = llm.chat(messages)
            msg = getattr(result, "message", None)
            content = getattr(msg, "content", None) if msg is not None else None
            return content if isinstance(content, str) and content.strip() else str(result)

        raise RuntimeError("Configured LLM does not support complete/chat")
    except Exception as e:
        raise RuntimeError(f"Error during direct query execution: {str(e)}")



def run_batch_queries_parallel(queries: list[str], collection_name: str, db_type: VectorDBType):
    """
    Run multiple queries in parallel
    """

    index = VectorDBFactory.create_index(
        db_type=db_type,
        mode=CollectionMode.APPEND_TO_EXISTING,
        collection_name=collection_name
    )

    retriever = get_retriever(index)
    query_engine = build_query_engine(retriever)

    def process_query(q):
        return query_engine.query(q)

    responses = [None] * len(queries)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_query, q): i for i, q in enumerate(queries)}

        for future in as_completed(futures):
            idx = futures[future]
            responses[idx] = future.result()

    return responses