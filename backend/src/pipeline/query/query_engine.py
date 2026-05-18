from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine, CitationQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever

# Updated imports (version-safe)
try:
    from llama_index.postprocessor.sentence_transformer_rerank import SentenceTransformerRerank
except ImportError:
    from llama_index.core.postprocessor import SentenceTransformerRerank

try:
    from llama_index.postprocessor.llm_rerank import LLMRerank
except ImportError:
    from llama_index.core.postprocessor import LLMRerank

# Compression (optional)
try:
    from llama_index.postprocessor.longllmlingua import LongLLMLinguaPostprocessor
    LONG_LINGUA_AVAILABLE = True
except ImportError:
    LONG_LINGUA_AVAILABLE = False

from src.pipeline.config.llm_settings_state import ensure_active_llm_settings_loaded
from .prompt import qa_prompt


def _to_int(value, default, minimum=1, maximum=20):
    try:
        return max(minimum, min(maximum, int(value)))
    except Exception:
        return default


def _safe_default_target_tokens(max_tokens: int) -> int:
    return max(128, min(2048, max_tokens // 2))


def build_query_engine(retriever, engine_settings_overrides=None, top_k=None, user_id: int = 1):
    """
    Build a robust query engine with:
    - Multi-query fusion
    - Reranking
    - Context compression
    - Optional streaming + citations
    
    Settings are fetched from user's LLMSettingsState in database (includes all retrieval config)
    and merged with optional runtime overrides from client.
    """

    # -------------------------------
    # 1. Merge settings (database + client overrides)
    # -------------------------------
    # Fetch user's saved settings from database (includes LLM + retrieval config)
    saved_settings = ensure_active_llm_settings_loaded(user_id=user_id).to_dict()
    # Optional runtime overrides from client
    runtime_settings = engine_settings_overrides if isinstance(engine_settings_overrides, dict) else {}
    # Merge: database defaults + client overrides (client takes priority)
    merged_settings = {**saved_settings, **runtime_settings}

    final_top_k = _to_int(
        top_k if top_k is not None else merged_settings.get("defaultTopK", 5),
        default=5,
    )

    max_tokens = _to_int(
        merged_settings.get("maxTokens", 1024),
        default=1024,
        minimum=64,
        maximum=16384,
    )

    use_reranking = bool(merged_settings.get("reranking", False))
    use_multi_query = bool(merged_settings.get("multiQuery", True))
    use_compression = bool(merged_settings.get("compression", False))
    stream_responses = bool(merged_settings.get("streamResponses", False))

    # -------------------------------
    # 2. Response synthesizer
    # -------------------------------
    response_synthesizer = get_response_synthesizer(
        text_qa_template=qa_prompt,
        streaming=stream_responses,
       
    )

    # -------------------------------
    # 3. Postprocessors
    # -------------------------------
    node_postprocessors = []

    # 🔹 Reranking
    if use_reranking:
        try:
            encoder_reranker = SentenceTransformerRerank(
                model="cross-encoder/ms-marco-MiniLM-L-6-v2",
                top_n=final_top_k,
            )
            node_postprocessors.append(encoder_reranker)
        except Exception as exc:
            print(f"[query_engine] SentenceTransformerRerank disabled: {exc}")

        try:
            llm_reranker = LLMRerank(top_n=final_top_k)
            node_postprocessors.append(llm_reranker)
        except Exception as exc:
            print(f"[query_engine] LLMRerank disabled: {exc}")

    # -------------------------------
    # 4. Multi-query fusion
    # -------------------------------
    active_retriever = retriever

    if use_multi_query:
        try:
            active_retriever = QueryFusionRetriever(
                [retriever],
                similarity_top_k=final_top_k,
                num_queries=4,
                use_async=False,  # safer (avoid event loop issues)
            )
        except Exception as exc:
            print(f"[query_engine] QueryFusion disabled: {exc}")
            active_retriever = retriever

    # -------------------------------
    # 5. Context compression
    # -------------------------------
    if use_compression and LONG_LINGUA_AVAILABLE:
        target_tokens = _to_int(
            merged_settings.get(
                "contextTargetTokens",
                _safe_default_target_tokens(max_tokens),
            ),
            default=_safe_default_target_tokens(max_tokens),
            minimum=128,
            maximum=4096,
        )

        try:
            lingua_compressor = LongLLMLinguaPostprocessor(
                instruction_str="Extract only relevant information.",
                target_token=target_tokens,
                rank_method="longllmlingua",
            )
            node_postprocessors.append(lingua_compressor)
        except Exception as exc:
            print(f"[query_engine] LongLLMLingua disabled: {exc}")

    elif use_compression:
        print("[query_engine] LongLLMLingua not installed → skipping compression")

    # -------------------------------
    # 6. Build query engine
    # -------------------------------
    if stream_responses:
        query_engine = CitationQueryEngine(
            retriever=active_retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=node_postprocessors,
            citation_chunk_size=512,
            # streaming=True,
        )
    else:
        query_engine = RetrieverQueryEngine(
            retriever=active_retriever,  # ✅ FIXED
            response_synthesizer=response_synthesizer,
            node_postprocessors=node_postprocessors,
        )

    # -------------------------------
    # 7. Debug logs
    # -------------------------------
    print("\n[Query Engine Config]")
    print(f"top_k={final_top_k}")
    print(f"reranking={use_reranking}")
    print(f"multi_query={use_multi_query}")
    print(f"compression={use_compression}")
    print(f"streaming={stream_responses}")
    print(f"postprocessors={len(node_postprocessors)}\n")

    return query_engine