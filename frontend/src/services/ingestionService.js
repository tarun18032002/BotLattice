function authHeaders(token) {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function runIngestionPipeline(chunking, collection, files, onMessage, token) {
  let totalChunks = 0;
  let totalDocuments = 0;

  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("chunking", JSON.stringify(chunking));
    formData.append("collection", JSON.stringify(collection));

    const response = await fetch("http://127.0.0.1:8000/ingest", {
      method: "POST",
      headers: {
        ...authHeaders(token),
      },
      body: formData
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Ingest failed (${response.status}): ${err}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    let fileChunks = 0;
    let fileDocuments = 0;

    const processLine = (line) => {
      if (!line.trim()) return;
      try {
        const parsed = JSON.parse(line);
        if (parsed.msg) onMessage(parsed.msg, parsed.level || "info", parsed);

        // Prefer explicit counters from stream metadata whenever present.
        if (Number.isFinite(Number(parsed.chunks))) {
          fileChunks = Number(parsed.chunks);
        }
        if (Number.isFinite(Number(parsed.documents))) {
          fileDocuments = Number(parsed.documents);
        }

        // Some backends only send counters in the final done packet.
        if (parsed.done) {
          if (Number.isFinite(Number(parsed.chunks))) fileChunks = Number(parsed.chunks);
          if (Number.isFinite(Number(parsed.documents))) fileDocuments = Number(parsed.documents);
        }
      } catch (err) {
        console.warn("Stream parse error", err);
      }
    };

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        // Process any trailing buffered line that might not end with a newline.
        if (buffer.trim()) processLine(buffer);
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        processLine(line);
      }
    }

    totalChunks += fileChunks;
    totalDocuments += fileDocuments;
  }

  return { chunks: totalChunks, documents: totalDocuments };
}
