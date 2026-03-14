// export async function runIngestionPipeline(config, files, log) {
//   let totalChunks = 0;

//   for (const file of files) {
//     log(`Uploading ${file.name}...`);

//     const formData = new FormData();
    

//     formData.append("file", file);
//     formData.append("collection_name", config.collectionName);

//     // // Chunking
//     // formData.append("chunk_strategy", config.chunkStrategy);
//     // formData.append("chunk_size", config.chunkSize);
//     // formData.append("chunk_overlap", config.chunkOverlap);

//     // // Embedding
//     // formData.append("embed_provider", config.embedProvider);
//     // formData.append("embed_model", config.embedModel);

//     // // Vector DB
//     // formData.append("vector_db", config.vectorDB);

//     const res = await fetch("http://localhost:8000/ingest", {
//       method: "POST",
//       body: formData,
//     });

//     if (!res.ok) {
//       throw new Error(`Failed ingesting ${file.name}`);
//     }

//     const data = await res.json();

//     log(`✔ ${file.name} ingested`, "success");

//     if (data.chunks) totalChunks += data.chunks;
//   }

//   return { chunks: totalChunks };
// }


export async function runIngestionPipeline(config, files, log) {

  let totalChunks = 0;

  for (const file of files) {

    const formData = new FormData();
    formData.append("file", file);
    formData.append("collection_name", config.collectionName);

    const res = await fetch("http://localhost:8000/ingest", {
      method: "POST",
      body: formData
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {

      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n");

      for (const line of lines) {

        if (!line.trim()) continue;

        const data = JSON.parse(line);

        if (data.msg) {
          log(data.msg, data.level || "info");
        }

        if (data.done) {
          totalChunks += data.chunks || 0;
        }

      }
    }
  }

  return { chunks: totalChunks };
}