export async function runIngestionPipeline(chunking, collection, files, onMessage) {
  let totalChunks = 0;

  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("chunking", JSON.stringify(chunking));
    formData.append("collection", JSON.stringify(collection));

    const response = await fetch("http://localhost:8000/ingest", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Ingest failed (${response.status}): ${err}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          if (parsed.msg) onMessage(parsed.msg, parsed.level || "info");
          if (parsed.done) totalChunks += parsed.chunks || 0;
        } catch (err) {
          console.warn("Stream parse error", err);
        }
      }
    }
  }

  return { chunks: totalChunks };
}
