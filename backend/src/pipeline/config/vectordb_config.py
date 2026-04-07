VECTORDB_OPTIONS = {

    "qdrant": {
        "fields": [
            {
                "name": "url",
                "type": "str",
                "required": True,
                "default": 'https://{qdrant_id}.eu-west-1-0.aws.cloud.qdrant.io:6333',
                "description": "Qdrant DB URL"
            },
            {
                "name": "api key",
                "type": "str",
                "required": True,
                "default": "lkjfdsxc vbnlythrdcblfcgblhvbb",
                "description": "Qdrant DB API KEY"
            },
            {
                "name": "Distance metric",
                "type": "str",
                "required": True,
            },
            {
                "name": "Hybrid search (BM25 + vector)",
                "type": "bool",
                "required": False,
                "default": False,
                "description":"Combine sparse lexical and dense semantic retrieval"
            },
            {
                "name": "Hybrid search (BM25 + vector)",
                "type": "bool",
                "required": False,
                "default": False,
                "description":"Attach source, page number, and timestamp to each chunk"
            }
        ]
    },
    "chroma":{
        "fields":[
            {"description":"Currently unavalible"}
        ]
    },

    "pinecone": {
        "fields": [
            {"description":"Currently unavalible"}
        ]
    },
}