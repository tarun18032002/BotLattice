from src.pipeline.config.vector_store import VectorDBFactory
from src.pipeline.config.enums import VectorDBType, CollectionMode
from src.pipeline.query.retriever import get_retriever
from src.pipeline.query.query_engine import build_query_engine
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.pipeline.config.llm_settings_state import ensure_active_llm_settings_loaded
from src.pipeline.config.embedding_runtime import ensure_embed_model_ready
from src.pipeline.config.vectordb_state import ensure_active_vectordb_loaded
from llama_index.core import Settings


def _resolve_top_k(top_k, engine_settings_overrides, user_id: int = 1):
    """Resolve effective top_k by merging database settings with runtime overrides.
    
    Settings hierarchy:
    1. Explicit top_k parameter (highest priority)
    2. Database LLM settings (defaultTopK from user's saved config)
    3. Hardcoded default: 5
    
    Args:
        top_k: Client-provided top_k override
        engine_settings_overrides: Optional dict with query engine setting overrides
        user_id: User ID to fetch saved settings from database
    
    Note: All retrieval settings (reranking, multiQuery, compression, etc.) come from
    the user's LLMSettingsState in the database via ensure_active_llm_settings_loaded()
    """
    # Fetch user's saved settings from database
    saved_settings = ensure_active_llm_settings_loaded(user_id=user_id).to_dict()
    # Optional runtime overrides from client
    runtime_settings = engine_settings_overrides if isinstance(engine_settings_overrides, dict) else {}
    # Merge: database defaults + client overrides (client takes priority)
    merged_settings = {**saved_settings, **runtime_settings}

    value = top_k if top_k is not None else merged_settings.get("defaultTopK", 5)
    try:
        return max(1, min(20, int(value)))
    except Exception:
        return 5

def run_query(
    query: str,
    collection_name: str,
    top_k=None,
    engine_settings_overrides=None,
    db_type=None,
    user_id: int = 1
):
    """Main RAG Query pipeline.
    
    Settings hierarchy (highest to lowest priority):
    1. Client-provided overrides (top_k, engine_settings_overrides)
    2. Database settings per user (embedding config, LLM settings + retrieval settings)
    3. Hardcoded defaults
    
    All retrieval settings come from user's LLMSettingsState in database:
    - defaultTopK, reranking, multiQuery, compression, simThreshold, etc.
    - These are fetched via ensure_active_llm_settings_loaded(user_id)
    - Client can optionally override them via engine_settings_overrides parameter
    """
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        if not isinstance(collection_name, str) or not collection_name.strip():
            raise ValueError("collection_name must be a non-empty string")

        query = query.strip()
        collection_name = collection_name.strip()

        # Ensure embed model is available even if startup warm-up is still running.
        ensure_embed_model_ready()

        # user_embedding = EmbeddingConfig.load(user_id=user_id)
        vectortState =ensure_active_vectordb_loaded(user_id=user_id)  # Ensure vector DB state is loaded for this user
        # print(f"User {user_id} embedding config: connected={user_embedding.connected}, provider='{user_embedding.provider}', model='{user_embedding.model}', dimension={user_embedding.dimension}")
        
        # Use provided db_type or determine from embedding config
        if db_type is None:
            db_type = vectortState.vectordb_type.lower() if vectortState.connected else "qdrant"
        
        print(f"Running RAG query: '{query}' against collection '{collection_name}' using DB '{db_type}'")
        
        # Get embedding dimension from collection metadata (stored when collection was created)
        embed_dim = VectorDBFactory.get_collection_dimension(db_type, collection_name)
        
        # Connect to existing vector store
        index = VectorDBFactory.create_index(
            db_type=db_type,
            mode=None,
            collection_name=collection_name,
            dim=embed_dim 
        )

        print(f"index of type {type(index)} created successfully for collection '{collection_name}'")
        effective_top_k = _resolve_top_k(top_k, engine_settings_overrides, user_id=user_id)
        # Create retriever
        retriever = get_retriever(index, similarity_top_k=effective_top_k)

        # Create query engine
        # Note: All retrieval settings (reranking, multiQuery, etc.) come from database per user
        query_engine = build_query_engine(
            retriever,
            engine_settings_overrides=engine_settings_overrides,
            top_k=effective_top_k,
            user_id=user_id,
        )

        # Run query
        response = query_engine.query(query)

        return response
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Error during query execution: {str(e)}\n{traceback_str}")
        raise RuntimeError(f"Error during query execution: {str(e)}")


def run_direct_query(query: str, system_prompt: str | None = None, user_id: int = 1):
    """Run a direct (non-RAG) LLM completion."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        saved = ensure_active_llm_settings_loaded(user_id=user_id).to_dict()
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