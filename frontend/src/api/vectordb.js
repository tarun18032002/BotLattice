export async function fetchVectordbOptions(type) {
  const res = await fetch(`http://localhost:8000/vectordb/options/${type}`,{
    method: 'GET',
  }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch chunking options");
  }

  return res.json();
}