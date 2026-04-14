import { useEffect, useState, useCallback } from "react";
import { fetchCollections, deleteCollection as apiDeleteCollection } from "../api/vectordb";

export function useCollections() {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCollections();
      setCollections(data);
    } catch (err) {
      console.error("Error fetching collections:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const removeCollection = useCallback(async (name) => {
    await apiDeleteCollection(name);
    setCollections((prev) => prev.filter((c) => c.name !== name));
  }, []);

  return { collections, loading, error, refresh: load, removeCollection };
}