export async function fetchChunkingOptions(type) {
  const res = await fetch(`http://localhost:8000/chunking/options/${type}`,{
    method: 'GET',
  }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch chunking options");
  }

  return res.json();
}