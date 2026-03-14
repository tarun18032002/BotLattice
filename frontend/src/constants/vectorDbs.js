export const VECTOR_DBS = [
  { value: "chroma",     label: "Chroma" },
  { value: "pinecone",   label: "Pinecone" },
  { value: "qdrant",     label: "Qdrant" },
  { value: "weaviate",   label: "Weaviate" },
  { value: "faiss",      label: "FAISS (local)" },
  { value: "milvus",     label: "Milvus" },
  { value: "pgvector",   label: "pgvector (Postgres)" },
  { value: "opensearch", label: "OpenSearch" },
];

export const VDB_DEFAULTS = {
  chroma:     { host: "localhost:8000",              keyNote: "No key needed" },
  pinecone:   { host: "https://index.pinecone.io",   keyNote: "Required" },
  qdrant:     { host: "localhost:6333",              keyNote: "Optional" },
  weaviate:   { host: "localhost:8080",              keyNote: "Optional" },
  faiss:      { host: "./faiss_index",               keyNote: "Local path" },
  milvus:     { host: "localhost:19530",             keyNote: "Optional" },
  pgvector:   { host: "postgresql://localhost/vecs", keyNote: "Optional" },
  opensearch: { host: "localhost:9200",              keyNote: "Optional" },
};

export const DISTANCE_METRICS = ["Cosine", "Euclidean (L2)", "Dot product", "Manhattan"];

export const DEFAULT_VECTOR_DB = "chroma";
