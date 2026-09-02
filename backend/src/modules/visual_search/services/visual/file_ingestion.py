import asyncio
import json
import pandas as pd
import requests
from io import BytesIO
from uuid import uuid4
from typing import List, Dict, Any, Optional
from sqlalchemy.future import select

# Internal Modules
from backend.src.modules.visual_search.models.ingestion import IngestionJob  # JobStatus removed
from backend.src.modules.visual_search.services.visual.engine import get_image_embedding
from backend.src.modules.visual_search.services.vector_store.factory import get_visual_vector_store

# --- CONFIG ---
BATCH_SIZE = 100
MAX_WORKERS = 20
VECTOR_SIZE = 512  # CLIP embedding size


async def update_job_safe(db_factory, job_id: int, status: str, processed=0, total=0, error=None, message=None):
    """Job status ko safely database mein update karta hai."""
    try:
        async with db_factory() as db:
            result = await db.execute(select(IngestionJob).where(IngestionJob.id == job_id))
            job = result.scalars().first()
            if job:
                job.status = status
                job.items_processed = processed
                job.total_items = total
                if error:
                    job.error_message = str(error)
                if message:
                    print(f"📝 Job Log: {message}")
                await db.commit()
    except Exception as e:
        print(f"⚠️ Status Update Failed: {e}")


async def parse_file_headers(file_content: bytes, filename: str) -> List[str]:
    """CSV ya JSON file ke headers/keys return karta hai."""
    if filename.endswith('.csv'):
        df = pd.read_csv(BytesIO(file_content), nrows=1)
        return list(df.columns)
    elif filename.endswith('.json'):
        data = json.loads(file_content.decode('utf-8'))
        if isinstance(data, list) and len(data) > 0:
            return list(data[0].keys())
        elif isinstance(data, dict):
            return list(data.keys())
        else:
            return []
    else:
        raise ValueError("Unsupported file format. Only CSV and JSON allowed.")


def _download_and_vectorize(image_url: str) -> Optional[List[float]]:
    """Image URL se download karke CLIP embedding generate karta hai."""
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None
        image_bytes = response.content
        vector = get_image_embedding(image_bytes)
        if not vector or len(vector) != VECTOR_SIZE:
            return None
        return vector
    except Exception:
        return None


async def process_file_upload(
    user_id: str,
    job_id: int,
    file_content: bytes,
    filename: str,
    field_mapping: Dict[str, str],
    db_factory
):
    """
    CSV/JSON file upload ke liye background task:
    1. File parse karein (title, slug, image_url fields)
    2. Har row ki image download karke embedding banayein
    3. Vector store mein upsert karein
    4. Progress update karein
    """
    print(f"🚀 [FileIngestion] Starting file processing for User: {user_id}, Job: {job_id}")

    try:
        await update_job_safe(db_factory, job_id, "processing")

        # 1. Parse file according to field_mapping
        if filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
            rows = df.to_dict(orient='records')
        elif filename.endswith('.json'):
            data = json.loads(file_content.decode('utf-8'))
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                rows = [data]
            else:
                raise ValueError("JSON file must be an array of objects or a single object.")
        else:
            raise ValueError("Unsupported file format. Only CSV and JSON allowed.")

        total_items = len(rows)
        await update_job_safe(db_factory, job_id, "processing", total=total_items, processed=0)

        # 2. Get vector store adapter (user's own credentials)
        async with db_factory() as db:
            from backend.src.shared.models.integration import UserIntegration
            stmt = select(UserIntegration).where(
                UserIntegration.user_id == str(user_id),
                UserIntegration.provider.in_(["qdrant", "mongodb"]),
                UserIntegration.is_active == True
            )
            result = await db.execute(stmt)
            integration = result.scalars().first()

        if not integration:
            await update_job_safe(db_factory, job_id, "failed", error="No active vector DB integration found.")
            return

        credentials = json.loads(integration.credentials)
        collection_name = credentials.get("visual_collection_name", "visual_search_products")

        vector_store = get_visual_vector_store(credentials=credentials)

        # Ensure collection exists
        if not await vector_store.collection_exists(collection_name):
            await vector_store.create_collection(collection_name, VECTOR_SIZE, "cosine")

        # 3. Process each row
        processed_count = 0
        points_batch = []

        for row in rows:
            # Extract fields using mapping
            title = row.get(field_mapping.get("title", "title"))
            slug = row.get(field_mapping.get("slug", "slug"))
            image_url = row.get(field_mapping.get("image_url", "image_url"))

            if not title or not image_url:
                continue

            # Download and vectorize image
            vector = await asyncio.to_thread(_download_and_vectorize, image_url)
            if vector is None:
                continue

            # Prepare point for upsert
            point = {
                "id": str(uuid4()),
                "vector": vector,
                "payload": {
                    "product_id": str(row.get(field_mapping.get("product_id", "product_id"), uuid4())),
                    "slug": slug,
                    "image_url": image_url,
                    "title": title,
                    "user_id": str(user_id),
                    "source": "file_upload"
                }
            }
            points_batch.append(point)

            # Batch upsert
            if len(points_batch) >= BATCH_SIZE:
                await vector_store.upsert(collection_name=collection_name, points=points_batch)
                processed_count += len(points_batch)
                await update_job_safe(db_factory, job_id, "processing", processed=processed_count, total=total_items)
                print(f"   -> Batch upserted. ({processed_count}/{total_items})")
                points_batch = []

        # Upsert remaining points
        if points_batch:
            await vector_store.upsert(collection_name=collection_name, points=points_batch)
            processed_count += len(points_batch)

        # Final status update
        await update_job_safe(db_factory, job_id, "completed", processed=processed_count, total=total_items, message=f"File processing complete. Processed {processed_count} items.")
        print(f"🎉 [FileIngestion] Completed. Processed {processed_count} items.")

    except Exception as e:
        print(f"❌ [FileIngestion] Job failed: {e}")
        await update_job_safe(db_factory, job_id, "failed", error=str(e))