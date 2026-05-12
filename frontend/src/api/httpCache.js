const inFlight = new Map();
const cache = new Map();

const DEFAULT_TTL_MS = 1500;

function buildKey(method, url) {
  return `${method.toUpperCase()} ${url}`;
}

export async function getJson(url, options = {}) {
  const method = "GET";
  const key = buildKey(method, url);
  const now = Date.now();
  const ttlMs = options.ttlMs ?? DEFAULT_TTL_MS;

  const cached = cache.get(key);
  if (cached && now - cached.timestamp < ttlMs) {
    return cached.data;
  }

  if (inFlight.has(key)) {
    return inFlight.get(key);
  }

  const promise = fetch(url, { method }).then(async (res) => {
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      const detail = data?.detail || options.errorMessage || "Request failed";
      const error = new Error(detail);
      error.status = res.status;
      throw error;
    }

    const data = await res.json();
    cache.set(key, { data, timestamp: Date.now() });
    return data;
  }).finally(() => {
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
}

export function invalidateGetCache(urlPrefix = "") {
  for (const key of cache.keys()) {
    if (!urlPrefix || key.includes(urlPrefix)) {
      cache.delete(key);
    }
  }
}
