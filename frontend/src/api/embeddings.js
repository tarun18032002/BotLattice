const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson, invalidateGetCache } from "./httpCache";

function authHeaders(token) {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

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

export async function fetchCurrentEmbedding(token) {
  const res = await fetch(`${API_BASE_URL}/embeddings/current/`, {
    method: "GET",
    headers: {
      ...authHeaders(token),
    },
  });

  if (res.status === 404) {
    return null;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || "Failed to fetch current embedding config";
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }

  if (data?.connected === false) {
    return null;
  }

  return data;
}

export async function connectEmbedding(payload, token) {
  const params = new URLSearchParams();
  params.set("provider", payload.provider);
  params.set("model", payload.model);

  if (payload.apiKey) params.set("api_key", payload.apiKey);
  if (payload.batchSize !== undefined) params.set("batch_size", String(payload.batchSize));
  if (payload.normalize !== undefined) params.set("normalize", String(Boolean(payload.normalize)));
  if (payload.cache !== undefined) params.set("cache", String(Boolean(payload.cache)));

  const res = await fetch(`${API_BASE_URL}/embeddings/connect/?${params.toString()}`, {
    method: "POST",
    headers: {
      ...authHeaders(token),
    },
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data?.detail || "Failed to connect embedding model";
    throw new Error(message);
  }

  invalidateGetCache("/embeddings/");

  return data;
}
