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
  { value: "fixed",     label: "Fixed Size",          desc: "Split by exact token count" },
  { value: "recursive", label: "Recursive Character", desc: "Split by character hierarchy" },
  { value: "sentence",  label: "Sentence Splitter",   desc: "Preserve sentence boundaries" },
  { value: "semantic",  label: "Semantic Chunking",   desc: "Group by meaning similarity" },
  { value: "token",     label: "Token-based",         desc: "Tiktoken or HF tokenizer" },
  { value: "markdown",  label: "Markdown Header",     desc: "Split on # / ## headings" },
  { value: "paragraph", label: "Paragraph",           desc: "Split on blank lines" },
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
