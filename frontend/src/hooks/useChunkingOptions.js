import { useEffect, useState } from "react";
import { fetchChunkingOptions } from "../api/chunking";

export function useChunkingOptions(chunkStrategy) {
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!chunkStrategy) return;

    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchChunkingOptions(chunkStrategy);
        setFields(data.fields || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [chunkStrategy]);

  return { fields, loading };
}