from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VisualVectorStore(ABC):
    """
    Abstract Base Class for all Vector Database Adapters.
    Any vector DB (Qdrant, MongoDB Atlas, Pinecone, etc.) must implement these methods.
    """

    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """Check karein collection maujood hai ya nahi."""
        pass

    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int, distance: str = "cosine") -> None:
        """Nayi collection banayein (vector size + distance metric ke saath)."""
        pass

    @abstractmethod
    async def upsert(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        """
        Points upsert karein.
        points = [
            {
                "id": "uuid",
                "vector": [0.1, 0.2, ...],
                "payload": {"product_id": "...", "slug": "...", "image_url": "..."}
            },
            ...
        ]
        """
        pass

    @abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Similarity search karein.
        filters: e.g., {"user_id": "123"}
        Return: [{"id": "...", "score": 0.89, "payload": {...}}, ...]
        """
        pass

    @abstractmethod
    async def scroll(
        self,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        offset: Optional[int] = None
    ) -> tuple[List[Dict[str, Any]], Optional[int]]:
        """
        Large collections ko page-by-page padhein (sync ke liye).
        Return: (list_of_points, next_offset)
        """
        pass

    @abstractmethod
    async def delete(self, collection_name: str, ids: List[str]) -> None:
        """IDs ke hisaab se points delete karein."""
        pass