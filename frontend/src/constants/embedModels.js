export const EMBED_PROVIDERS = [
  { value: "openai",      label: "OpenAI" },
  { value: "cohere",      label: "Cohere" },
  { value: "huggingface", label: "HuggingFace" },
  { value: "voyage",      label: "Voyage AI" },
  { value: "google",      label: "Google Gemini" },
  { value: "mistral",     label: "Mistral" },
  { value: "local",       label: "Local / Ollama" },
];

export const EMBED_MODELS = {
  openai:      ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
  cohere:      ["embed-english-v3.0", "embed-multilingual-v3.0", "embed-english-light-v3.0"],
  huggingface: ["BAAI/bge-large-en-v1.5", "sentence-transformers/all-MiniLM-L6-v2", "thenlper/gte-large", "intfloat/multilingual-e5-large"],
  voyage:      ["voyage-3", "voyage-3-lite", "voyage-finance-2", "voyage-code-3"],
  google:      ["text-embedding-004", "embedding-001"],
  mistral:     ["mistral-embed"],
  local:       ["nomic-embed-text", "mxbai-embed-large", "all-minilm", "llama3:latest"],
};

export const DEFAULT_EMBED_PROVIDER = "openai";
export const DEFAULT_EMBED_MODEL    = "text-embedding-3-small";
