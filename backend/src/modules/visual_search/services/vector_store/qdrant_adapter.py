import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from backend.src.modules.visual_search.services.vector_store.base import VisualVectorStore


class QdrantVisualAdapter(VisualVectorStore):
    """
    Qdrant (Cloud ya Local) ke liye Visual Search Adapter.
    Ye VisualVectorStore base class ko implement karta hai.
    """

    def __init__(self, url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        Qdrant client initialize karein.

        Args:
            url: Qdrant Cloud URL (https://xyz.cloud.qdrant.io) ya local (http://localhost:6333)
            api_key: Qdrant API key (Cloud ke liye zaroori)
            timeout: Connection timeout (seconds)
        """
        self.client = QdrantClient(url=url, api_key=api_key, timeout=timeout)
        print(f"✅ [QdrantAdapter] Connected to: {url}")

    async def collection_exists(self, collection_name: str) -> bool:
        """Check karein collection maujood hai ya nahi."""
        def _check():
            try:
                self.client.get_collection(collection_name)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_check)

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "cosine"
    ) -> None:
        """Nayi collection banayein (vector size + distance metric ke saath)."""
        def _create():
            # Distance metric mapping
            distance_map = {
                "cosine": qmodels.Distance.COSINE,
                "euclidean": qmodels.Distance.EUCLID,
                "dot": qmodels.Distance.DOT,
            }
            dist = distance_map.get(distance.lower(), qmodels.Distance.COSINE)

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=dist
                )
            )

            # Payload index for faster filtering (user_id, product_id, etc.)
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="user_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD
            )
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="product_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD
            )

        await asyncio.to_thread(_create)
        print(f"✅ [QdrantAdapter] Collection '{collection_name}' created with size={vector_size}")

    async def upsert(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        """
        Points upsert karein.
        points = [{"id": "uuid", "vector": [0.1, ...], "payload": {...}}]
        """
        def _upsert():
            qdrant_points = []
            for p in points:
                qdrant_points.append(
                    qmodels.PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p.get("payload", {})
                    )
                )
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )

        await asyncio.to_thread(_upsert)
        print(f"✅ [QdrantAdapter] Upserted {len(points)} points to '{collection_name}'")

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
        Return: [{"id": "...", "score": 0.89, "payload": {...}}]
        """
        def _search():
            # Build filter
            qdrant_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key=key,
                            match=qmodels.MatchValue(value=str(value))
                        )
                    )
                qdrant_filter = qmodels.Filter(must=must_conditions)

            # Execute search
            response = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True,
                query_filter=qdrant_filter,
                score_threshold=score_threshold
            )

            results = []
            for hit in response.points:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload or {}
                })
            return results

        return await asyncio.to_thread(_search)

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
        def _scroll():
            # Build filter
            qdrant_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key=key,
                            match=qmodels.MatchValue(value=str(value))
                        )
                    )
                qdrant_filter = qmodels.Filter(must=must_conditions)

            # Scroll through points
            records, next_offset = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=qdrant_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                offset=offset
            )

            points = []
            for rec in records:
                points.append({
                    "id": rec.id,
                    "payload": rec.payload or {}
                })
            return points, next_offset

        return await asyncio.to_thread(_scroll)

    async def delete(self, collection_name: str, ids: List[str]) -> None:
        """IDs ke hisaab se points delete karein."""
        def _delete():
            self.client.delete(
                collection_name=collection_name,
                points_selector=qmodels.PointIdsList(points=ids)
            )

        await asyncio.to_thread(_delete)
        print(f"✅ [QdrantAdapter] Deleted {len(ids)} points from '{collection_name}'")