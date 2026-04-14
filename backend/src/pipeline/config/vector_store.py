import os
import json

# LlamaIndex Core
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.vector_stores.types import BasePydanticVectorStore

# Individual Vector Stores
from llama_index.vector_stores.qdrant import QdrantVectorStore
# from llama_index.vector_stores.pinecone import PineconeVectorStore
# from llama_index.vector_stores.faiss import FaissVectorStore

# DB Specific Clients
import qdrant_client
# from pinecone import Pinecone
# import faiss

from src.pipeline.config.enums import VectorDBType,CollectionMode
from src.pipeline.config.vectordb_state import active_vectordb


class VectorDBFactory:
    """Factory to create and manage connections to different Vector DBs."""

    @staticmethod
    def _normalize_db_type(db_type: VectorDBType | str) -> VectorDBType:
        if isinstance(db_type, VectorDBType):
            return db_type
        return VectorDBType(db_type)
    
    @staticmethod
    def get_vector_store(
        db_type: VectorDBType, 
        collection_name: str, 
        dim: int = 1536,
        **kwargs
    ) -> BasePydanticVectorStore:
        db_type = VectorDBFactory._normalize_db_type(db_type)
        
        if db_type == VectorDBType.QDRANT:
            url = active_vectordb.url or "http://localhost:6333"
            api_key = active_vectordb.api_key
            print(f"The QDrant Url : {url}")
            client = qdrant_client.QdrantClient(
                url=url,
                api_key=api_key,
            )
            return QdrantVectorStore(client=client, collection_name=collection_name)

        # elif db_type == DBType.PINECONE:
        #     # Expects PINECONE_API_KEY in env
        #     pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        #     pinecone_index = pc.Index(collection_name)
        #     return PineconeVectorStore(pinecone_index=pinecone_index)

        # elif db_type == DBType.FAISS:
        #     # Local FAISS implementation
        #     faiss_index = faiss.IndexFlatL2(dim)
        #     return FaissVectorStore(faiss_index=faiss_index)

        else:
            raise ValueError(f"Unsupported DB type: {db_type}")
    

    @staticmethod
    def get_collections(db_type: VectorDBType):
        """
        Fetch all collection names from the configured vector DB
        """
        db_type = VectorDBFactory._normalize_db_type(db_type)

        if db_type == VectorDBType.QDRANT:
            import qdrant_client

            url = active_vectordb.url or "http://localhost:6333"
            api_key = active_vectordb.api_key
            client = qdrant_client.QdrantClient(
                url=url,
                api_key=api_key,
            )

            collections = client.get_collections()

            return [col.name for col in collections.collections]

        # elif db_type == VectorDBType.PINECONE:
        #     from pinecone import Pinecone
        #     pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        #     return pc.list_indexes()

        # elif db_type == VectorDBType.FAISS:
        #     # FAISS does not support collections
        #     return []

        else:
            raise ValueError(f"Unsupported DB type: {db_type}")

    @classmethod
    def _delete_collection(cls, db_type: VectorDBType, collection_name: str):
        """Delete a collection from the vector DB."""
        db_type = cls._normalize_db_type(db_type)
        if db_type == VectorDBType.QDRANT:
            url = active_vectordb.url or "http://localhost:6333"
            api_key = active_vectordb.api_key
            client = qdrant_client.QdrantClient(
                url=url,
                api_key=api_key,
            )
            client.delete_collection(collection_name)
        else:
            raise ValueError(f"Unsupported DB type for deletion: {db_type}")

    @classmethod
    def create_index(cls, db_type: VectorDBType,mode:CollectionMode | None, collection_name: str, nodes=None, dim=1536):
        """Prepares a LlamaIndex VectorStoreIndex ready for query or ingestion."""
        try:
            db_type = cls._normalize_db_type(db_type)
            vector_store = cls.get_vector_store(db_type, collection_name, dim=dim)

            if mode == CollectionMode.REPLACE_EXISTING:
                cls._delete_collection(db_type, collection_name)
                vector_store = cls.get_vector_store(db_type, collection_name, dim=dim)

            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            if nodes:
                return VectorStoreIndex(nodes, storage_context=storage_context)

            return VectorStoreIndex.from_vector_store(vector_store)
        except Exception as e:
            raise RuntimeError(f"Error creating index for collection '{collection_name}': {str(e)}")

    @classmethod
    def create_index_with_logs(
        cls,
        db_type: VectorDBType | str,
        mode: CollectionMode | None,
        collection_name: str,
        nodes=None,
        dim: int = 1536,
    ):
        """Yield ingestion progress logs and return the built index at the end."""
        db_type = cls._normalize_db_type(db_type)

        try:
            if mode == CollectionMode.REPLACE_EXISTING:
                yield json.dumps({
                    "msg": f"Collection '{collection_name}' already exists. Replacing it as per 'Replace_existing' mode.",
                    "level": "warning"
                }) + "\n"

            if nodes:
                yield json.dumps({
                    "msg": f"ingest nodes: {len(nodes)}",
                    "level": "info"
                }) + "\n"

            index = cls.create_index(
                db_type=db_type,
                mode=mode,
                collection_name=collection_name,
                nodes=nodes,
                dim=dim,
            )

            return index
        except Exception as e:
            yield json.dumps({
                "msg": f"Error creating index for collection '{collection_name}': {str(e)}",
                "level": "error"
            }) + "\n"
            raise

    