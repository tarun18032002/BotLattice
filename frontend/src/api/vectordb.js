export async function fetchVectordbOptions(type) {
  const res = await fetch(`http://localhost:8000/vector-db/options/${type}`,{
    method: 'GET',
  }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch chunking options");
  }

  return res.json();
}

function toNumber(value, fallback = 0) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function normalizeCollection(item) {
  if (typeof item === "string") {
    return { name: item, chunks: 0, docs: 0, db: "unknown", dim: 0, distance: "Unknown", status: "unknown" };
  }

  if (!item || typeof item !== "object") return null;

  const name = item.name ?? item.collection_name ?? item.collection;
  if (!name) return null;

  return {
    name,
    chunks:   toNumber(item.chunks ?? item.chunk_count, 0),
    docs:     toNumber(item.docs ?? item.document_count ?? item.doc_count, 0),
    db:       item.db ?? item.vector_db ?? item.database ?? "unknown",
    dim:      toNumber(item.dim ?? item.dimension, 0),
    distance: item.distance ?? "—",
    status:   item.status ?? "unknown",
  };
}

export async function fetchCollections() {
  const res = await fetch("http://127.0.0.1:8000/vector-db/collections", {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch vector database collections");
  }

  const data = await res.json();
  const rawCollections = Array.isArray(data.collections) ? data.collections : [];

  return rawCollections
    .map(normalizeCollection)
    .filter((collection) => Boolean(collection?.name));
}

export async function fetchVectordbProviders() {
  const res = await fetch("http://127.0.0.1:8000/vector-db/providers/");
  if (!res.ok) {
    throw new Error("Failed to fetch vector DB providers");
  }

  const data = await res.json();
  return Object.entries(data).map(([db, meta]) => ({
    db,
    requiresApiKey: Boolean(meta?.requires_api_key),
    showApiKey: meta?.show_api_key !== false,
    urlPlaceholder: meta?.url_placeholder || "",
  }));
}

export async function fetchCurrentVectordb() {
  const res = await fetch("http://127.0.0.1:8000/vector-db/current/");

  if (res.status === 404) {
    return null;
  }

  if (!res.ok) {
    throw new Error("Failed to fetch current vector DB config");
  }

  return res.json();
}

export async function deleteCollection(name) {
  const res = await fetch(`http://127.0.0.1:8000/vector-db/collections/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || "Failed to delete collection");
  return data;
}

export async function fetchCollectionDetail(name) {
  const res = await fetch(`http://127.0.0.1:8000/vector-db/collections/${encodeURIComponent(name)}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || "Failed to fetch collection detail");
  return normalizeCollection(data);
}

export async function connectVectordb(payload) {
  const params = new URLSearchParams();
  params.set("vectordb_type", payload.vectordbType);
  if (payload.url) params.set("url", payload.url);
  if (payload.apiKey) params.set("api_key", payload.apiKey);
  if (payload.distanceMetric) params.set("distance_metric", payload.distanceMetric);
  if (payload.hybridSearch !== undefined) params.set("hybrid_search", String(Boolean(payload.hybridSearch)));
  if (payload.storeMeta !== undefined) params.set("store_meta", String(Boolean(payload.storeMeta)));

  const res = await fetch(`http://127.0.0.1:8000/vector-db/connect/?${params.toString()}`, {
    method: "POST",
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data?.detail || "Failed to connect vector DB");
  }

  return data;
}