export async function runIngestionPipeline(apiConfig, files, log) {

  let totalChunks = 0;

  for (const file of files) {

    const formData = new FormData();

    formData.append("file", file);
    formData.append("config", JSON.stringify(apiConfig));

    const res = await fetch("http://localhost:8000/ingest", {
      method: "POST",
      body: formData
    });

    const reader = res.body.getReader();
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

          const data = JSON.parse(line);

          if (data.msg) {
            log(data.msg, data.level || "info");
          }

          if (data.done) {
            totalChunks += data.chunks || 0;
          }

        } catch (err) {
          console.error("Invalid JSON stream chunk:", line);
        }
      }
    }
  }

  return { chunks: totalChunks };
}