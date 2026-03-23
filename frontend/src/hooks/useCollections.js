import { useEffect, useState } from "react";

export function useCollections() {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCollections = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          "http://127.0.0.1:8000/vector-db/collections"
        );

        const data = await res.json();

        setCollections(data.collections || []);
      } catch (err) {
        console.error("Error fetching collections:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCollections();
  }, []);

  return { collections, loading };
}