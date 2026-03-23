CHUNKING_OPTIONS = {

    "sentence": {
        "fields": [
            {
                "name": "chunk_size",
                "type": "int",
                "required": True,
                "default": 512,
                "description": "Max tokens per chunk"
            },
            {
                "name": "chunk_overlap",
                "type": "int",
                "required": False,
                "default": 50,
            }
        ]
    },
    "token":{
        "fields":[
            {
                "name": "chunk_size",
                "type": "int",
                "required": True,
                "default": 512,
                "description": "Max tokens per chunk"
            },
            {
                "name": "chunk_overlap",
                "type": "int",
                "required": False,
                "default": 50,
            }
        ]
    },

    "code": {
        "fields": [
            {
                "name": "language",
                "type": "string",
                "required": True,
                "default": "python"
            },
            {
                "name": "chunk_lines",
                "type": "int",
                "required": True,
                "default": 40
            },
            {
                "name": "chunk_lines_overlap",
                "type": "int",
                "required": False,
                "default": 10
            }
        ]
    },

    "hierarchical": {
        "fields": [
            {
                "name": "chunk_sizes",
                "type": "list[int]",
                "required": True,
                "default": [2048, 512, 128]
            }
        ]
    },

    "html": {"fields": []},
    "markdown": {"fields": []},

    "simple": {
        "fields": [
            {
                "name": "chunk_size",
                "type": "int",
                "required": True,
                "default": 512,
                "description": "Max tokens per chunk"
            },
            {
                "name": "chunk_overlap",
                "type": "int",
                "required": False,
                "default": 50,
            }
        ]
    },
}