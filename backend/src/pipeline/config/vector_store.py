import os

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


class VectorDBFactory:
    """Factory to create and manage connections to different Vector DBs."""
    
    @staticmethod
    def get_vector_store(
        db_type: VectorDBType, 
        collection_name: str, 
        dim: int = 1536,
        **kwargs
    ) -> BasePydanticVectorStore:
        
        if db_type == VectorDBType.QDRANT:
            # Expects QDRANT_URL and QDRANT_API_KEY in env
            print(f"The QDrant Url : {os.getenv('QDRANT_URL')}")
            client = qdrant_client.QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
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

        if db_type == VectorDBType.QDRANT:
            import qdrant_client

            client = qdrant_client.QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
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
        if db_type == VectorDBType.QDRANT:
            client = qdrant_client.QdrantClient(
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )
            client.delete_collection(collection_name)
        else:
            raise ValueError(f"Unsupported DB type for deletion: {db_type}")

    @classmethod
    def create_index(cls, db_type: VectorDBType,mode:CollectionMode, collection_name: str, nodes=None, dim=1536):
        """Prepares a LlamaIndex VectorStoreIndex ready for query or ingestion."""
        vector_store = cls.get_vector_store(db_type, collection_name, dim=dim)
        
        # Handle overwrite
        if mode == "Replace_existing":
            cls._delete_collection(db_type,collection_name)
            vector_store = cls.get_vector_store(db_type,collection_name,dim=dim)

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        if nodes:
            # Ingestion mode
            print(f"----- ingest nodes,{len(nodes)}")
            return VectorStoreIndex(nodes, storage_context=storage_context)
        else:
            # Query mode (connect to existing)
            print(f"----- query nodes")
            return VectorStoreIndex.from_vector_store(vector_store)

    