const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson, invalidateGetCache } from "./httpCache";

export async function fetchEmbeddingProviders() {
  const data = await getJson(`${API_BASE_URL}/embeddings/providers/`, {
    errorMessage: "Failed to fetch embedding providers",
  });
  return Object.entries(data).map(([provider, value]) => {
    // Backward compatibility: value may be a plain model array.
    if (Array.isArray(value)) {
      return {
        provider,
        models: value,
        requiresApiKey: false,
      };
    }

    return {
      provider,
      models: Array.isArray(value?.models) ? value.models : [],
      requiresApiKey: Boolean(value?.requires_api_key),
    };
  });
}

export async function fetchCurrentEmbedding() {
  try {
    return await getJson(`${API_BASE_URL}/embeddings/current/`, {
      errorMessage: "Failed to fetch current embedding config",
    });
  } catch (err) {
    if (err?.status === 404) {
      return null;
    }
    throw err;
  }
}

export async function connectEmbedding(payload) {
  const params = new URLSearchParams();
  params.set("provider", payload.provider);
  params.set("model", payload.model);

  if (payload.apiKey) params.set("api_key", payload.apiKey);
  if (payload.batchSize !== undefined) params.set("batch_size", String(payload.batchSize));
  if (payload.normalize !== undefined) params.set("normalize", String(Boolean(payload.normalize)));
  if (payload.cache !== undefined) params.set("cache", String(Boolean(payload.cache)));

  const res = await fetch(`${API_BASE_URL}/embeddings/connect/?${params.toString()}`, {
    method: "POST",
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data?.detail || "Failed to connect embedding model";
    throw new Error(message);
  }

  invalidateGetCache("/embeddings/");

  return data;
}
