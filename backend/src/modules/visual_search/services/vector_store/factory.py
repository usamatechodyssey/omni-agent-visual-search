from typing import Dict, Any
from backend.src.modules.visual_search.services.vector_store.base import VisualVectorStore
from backend.src.modules.visual_search.services.vector_store.qdrant_adapter import QdrantVisualAdapter
from backend.src.modules.visual_search.services.vector_store.mongo_adapter import MongoVisualAdapter


def get_visual_vector_store(credentials: Dict[str, Any]) -> VisualVectorStore:
    """
    User ke credentials ke hisaab se sahi adapter return karega.
    
    credentials = {
        "provider": "qdrant" | "mongodb",
        "url": "...",  # for qdrant
        "api_key": "...",  # for qdrant
        "connection_string": "...",  # for mongodb
        "database_name": "..."  # for mongodb
    }
    """
    provider = credentials.get("provider", "qdrant").lower()
    
    if provider == "qdrant":
        url = credentials.get("url")
        api_key = credentials.get("api_key")
        if not url:
            raise ValueError("Qdrant URL is required.")
        return QdrantVisualAdapter(url=url, api_key=api_key)
    
    elif provider == "mongodb":
        connection_string = credentials.get("connection_string") or credentials.get("url")
        database_name = credentials.get("database_name", "visual_search")
        if not connection_string:
            raise ValueError("MongoDB connection string is required.")
        return MongoVisualAdapter(connection_string=connection_string, database_name=database_name)
    
    else:
        raise ValueError(f"Unsupported vector DB provider: {provider}")