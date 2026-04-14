export async function fetchEmbeddingProviders() {
  const res = await fetch("http://127.0.0.1:8000/embeddings/providers/");
  if (!res.ok) {
    throw new Error("Failed to fetch embedding providers");
  }

  const data = await res.json();
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
  const res = await fetch("http://127.0.0.1:8000/embeddings/current/");

  if (res.status === 404) {
    return null;
  }

  if (!res.ok) {
    throw new Error("Failed to fetch current embedding config");
  }

  return res.json();
}

export async function connectEmbedding(payload) {
  const params = new URLSearchParams();
  params.set("provider", payload.provider);
  params.set("model", payload.model);

  if (payload.apiKey) params.set("api_key", payload.apiKey);
  if (payload.batchSize !== undefined) params.set("batch_size", String(payload.batchSize));
  if (payload.normalize !== undefined) params.set("normalize", String(Boolean(payload.normalize)));
  if (payload.cache !== undefined) params.set("cache", String(Boolean(payload.cache)));

  const res = await fetch(`http://127.0.0.1:8000/embeddings/connect/?${params.toString()}`, {
    method: "POST",
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data?.detail || "Failed to connect embedding model";
    throw new Error(message);
  }

  return data;
}
