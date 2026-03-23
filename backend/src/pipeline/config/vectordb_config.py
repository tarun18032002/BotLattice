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