// ── LLM Providers & Models ────────────────────────────────────────────────────

export const LLM_PROVIDERS = [
  { value: "anthropic", label: "Anthropic" },
  { value: "openai",    label: "OpenAI" },
  { value: "groq",      label: "Groq" },
  { value: "ollama",    label: "Ollama (local)" },
  { value: "mistral",   label: "Mistral" },
];

export const LLM_MODELS = {
  anthropic: ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-4-5-20251001"],
  openai:    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  groq:      ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
  ollama:    ["llama3.2", "mistral", "phi3", "gemma2"],
  mistral:   ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
};

export const DEFAULT_LLM_PROVIDER = "anthropic";
export const DEFAULT_LLM_MODEL    = "claude-sonnet-4-20250514";

// ── Chunking Strategies ────────────────────────────────────────────────────────

export const CHUNK_STRATEGIES = [
  { value: "sentence", label: "Sentence", desc: "Split by sentences" },
  { value: "token", label: "Token", desc: "Token-based chunking" },
  { value: "code", label: "Code", desc: "Code-aware splitting" },
  { value: "html", label: "HTML", desc: "HTML structure parsing" },
  { value: "markdown", label: "Markdown", desc: "Markdown parsing" },
  { value: "hierarchical", label: "Hierarchical", desc: "Multi-level chunking" },
  { value: "simple", label: "Simple", desc: "Basic chunking" },
];

/** Returns which controls a strategy exposes */
export const getChunkControls = (strategy) => ({
  hasSize:      !["markdown", "paragraph"].includes(strategy),
  hasOverlap:   !["semantic", "paragraph", "markdown"].includes(strategy),
  hasBuffer:    strategy === "semantic",
  hasSeparator: strategy === "recursive",
});

export const DEFAULT_CHUNK_STRATEGY = "recursive";

// ── Default System Prompt ─────────────────────────────────────────────────────

export const DEFAULT_SYSTEM_PROMPT = `You are a precise RAG assistant with access to a knowledge base.

Rules:
1. Answer only from the retrieved context when in RAG mode
2. If context is insufficient, say so clearly
3. Always cite source documents when possible
4. Be concise and structured in your responses`;
