const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchChunkingOptions(type) {
  const res = await fetch(`${API_BASE_URL}/chunking/options/${type}`,{
    method: 'GET',
  }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch chunking options");
  }

  return res.json();
}