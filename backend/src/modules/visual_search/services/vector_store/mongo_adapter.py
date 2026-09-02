import asyncio
import json
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ReplaceOne
from pymongo.errors import CollectionInvalid, OperationFailure

from backend.src.modules.visual_search.services.vector_store.base import VisualVectorStore


class MongoVisualAdapter(VisualVectorStore):
    """
    MongoDB Atlas Vector Search ke liye Visual Search Adapter.
    User ke apne MongoDB database se connect karta hai.
    """

    def __init__(self, connection_string: str, database_name: str = "visual_search"):
        self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        self.db = self.client[database_name]
        print(f"✅ [MongoAdapter] Connected to DB: {database_name}")

    async def collection_exists(self, collection_name: str) -> bool:
        def _check():
            return collection_name in self.db.list_collection_names()
        return await asyncio.to_thread(_check)

    async def create_collection(self, collection_name: str, vector_size: int, distance: str = "cosine") -> None:
        def _create():
            try:
                self.db.create_collection(collection_name)
                print(f"✅ [MongoAdapter] Collection '{collection_name}' created.")
            except CollectionInvalid:
                print(f"ℹ️ [MongoAdapter] Collection '{collection_name}' already exists.")

            # Vector Search Index (sirf Atlas Cloud par chalta hai)
            try:
                index_name = "visual_embedding_index"
                index_definition = {
                    "mappings": {
                        "dynamic": True,
                        "fields": {
                            "embedding": {
                                "type": "knnVector",
                                "dimensions": vector_size,
                                "similarity": distance.upper()
                            }
                        }
                    }
                }
                existing_indexes = self.db[collection_name].list_indexes()
                index_exists = any(idx["name"] == index_name for idx in existing_indexes)
                if not index_exists:
                    self.db[collection_name].create_index(
                        [(index_name, "MongoDB Atlas Vector Search")],
                        name=index_name,
                        **index_definition
                    )
                    print(f"✅ [MongoAdapter] Vector index '{index_name}' created.")
                else:
                    print(f"ℹ️ [MongoAdapter] Vector index '{index_name}' already exists.")
            except OperationFailure as e:
                print(f"⚠️ [MongoAdapter] Vector index creation failed (Atlas only): {e}")
                self.db[collection_name].create_index(
                    [("embedding", "2dsphere")],
                    name="embedding_geo_index"
                )
        await asyncio.to_thread(_create)

    async def upsert(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        def _upsert():
            collection = self.db[collection_name]
            ops = []
            for p in points:
                doc = {
                    "embedding": p["vector"],
                    **p.get("payload", {})  # product_id, slug, image_url, user_id, etc.
                }
                # FIX: pymongo.ReplaceOne object use karein, raw dict nahi
                ops.append(ReplaceOne({"_id": p["id"]}, doc, upsert=True))
            if ops:
                collection.bulk_write(ops)
                print(f"✅ [MongoAdapter] Upserted {len(points)} points to '{collection_name}'")
        await asyncio.to_thread(_upsert)

    async def search(self, collection_name: str, query_vector: List[float], limit: int = 10, filters: Optional[Dict[str, Any]] = None, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        def _search():
            collection = self.db[collection_name]
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "visual_embedding_index",
                        "queryVector": query_vector,
                        "path": "embedding",
                        "numCandidates": limit * 10,
                        "limit": limit
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "score": {"$meta": "vectorSearchScore"},
                        "product_id": 1,
                        "slug": 1,
                        "image_url": 1,
                        "title": 1,
                        "price": 1,
                        "source": 1,
                        "user_id": 1
                    }
                }
            ]
            if filters:
                match_stage = {}
                for key, value in filters.items():
                    match_stage[key] = value
                pipeline.insert(0, {"$match": match_stage})

            results = list(collection.aggregate(pipeline))
            formatted_results = []
            for hit in results:
                score = hit.get("score", 0.0)
                if score_threshold is not None and score < score_threshold:
                    continue
                formatted_results.append({
                    "id": str(hit["_id"]),
                    "score": score,
                    "payload": {
                        "product_id": hit.get("product_id"),
                        "slug": hit.get("slug"),
                        "image_url": hit.get("image_url"),
                        "title": hit.get("title"),
                        "price": hit.get("price"),
                        "source": hit.get("source"),
                        "user_id": hit.get("user_id")
                    }
                })
            return formatted_results
        return await asyncio.to_thread(_search)

    async def scroll(self, collection_name: str, filters: Optional[Dict[str, Any]] = None, limit: int = 1000, offset: Optional[int] = None) -> tuple[List[Dict[str, Any]], Optional[int]]:
        def _scroll():
            collection = self.db[collection_name]
            query = filters or {}
            cursor = collection.find(query, {"_id": 1, "product_id": 1, "slug": 1, "image_url": 1}).skip(offset or 0).limit(limit)
            points = []
            for doc in cursor:
                points.append({
                    "id": str(doc["_id"]),
                    "payload": {
                        "product_id": doc.get("product_id"),
                        "slug": doc.get("slug"),
                        "image_url": doc.get("image_url")
                    }
                })
            next_offset = (offset or 0) + len(points)
            if len(points) < limit:
                next_offset = None
            return points, next_offset
        return await asyncio.to_thread(_scroll)

    async def delete(self, collection_name: str, ids: List[str]) -> None:
        def _delete():
            collection = self.db[collection_name]
            result = collection.delete_many({"_id": {"$in": ids}})
            print(f"✅ [MongoAdapter] Deleted {result.deleted_count} points from '{collection_name}'")
        await asyncio.to_thread(_delete)