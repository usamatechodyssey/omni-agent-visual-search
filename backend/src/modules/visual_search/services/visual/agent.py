import asyncio
import json
import requests
import concurrent.futures
from uuid import uuid4
from sqlalchemy.future import select

# Internal Modules
from backend.src.modules.visual_search.models.ingestion import IngestionJob
from backend.src.modules.visual_search.services.vector_store.factory import get_visual_vector_store
from backend.src.modules.visual_search.services.visual.engine import get_image_embedding, get_visual_model

# Connectors
from backend.src.modules.visual_search.services.connectors.shopify_connector import ShopifyConnector
from backend.src.modules.visual_search.services.connectors.woocommerce_connector import WooCommerceConnector
from backend.src.modules.visual_search.services.connectors.mongo_connector import MongoProductConnector
from backend.src.modules.visual_search.services.connectors.sanity_connector import SanityConnector

# Shared Imports
from backend.src.shared.models.user import User
from backend.src.shared.models.integration import UserIntegration

# --- OPTIMIZATION CONFIG ---
BATCH_SIZE = 100
MAX_WORKERS = 20
VECTOR_SIZE = 512


async def update_job_safe(db_factory, job_id: int, status: str, processed=0, total=0, error=None, message=None, details=None):
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
                if details:
                    job.details = details
                await db.commit()
    except Exception as e:
        print(f"⚠️ Status Update Failed: {e}")


def get_connector(provider: str, credentials: dict):
    if provider == 'shopify':
        return ShopifyConnector(credentials)
    elif provider == 'woocommerce':
        return WooCommerceConnector(credentials)
    elif provider == 'mongodb_store':
        return MongoProductConnector(credentials)
    elif provider == 'sanity':
        return SanityConnector(credentials)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def fetch_products_from_source(provider: str, credentials: dict):
    print(f"🔄 [Visual Agent] Fetching products from {provider}...")
    try:
        connector = get_connector(provider, credentials)
        return await asyncio.to_thread(connector.fetch_products)
    except Exception as e:
        print(f"❌ Fetch Error: {e}")
        return []


def download_and_vectorize(product):
    image_url = product.get('image_url')
    if not image_url:
        return None

    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None
        image_bytes = response.content
        vector = get_image_embedding(image_bytes)
        if not vector or len(vector) != VECTOR_SIZE:
            return None
        return {"product": product, "vector": vector}
    except Exception:
        return None


async def get_current_db_state(vector_store, collection_name: str, user_id: str):
    state = {}
    offset = None
    print(f"🕵️ Scanning existing data for User: {user_id} in '{collection_name}'...")
    while True:
        records, next_offset = await vector_store.scroll(
            collection_name=collection_name,
            filters={"user_id": str(user_id)},
            limit=1000,
            offset=offset
        )
        for point in records:
            payload = point.get("payload", {})
            prod_id = payload.get("product_id")
            img_url = payload.get("image_url")
            if prod_id and img_url:
                key = f"{prod_id}::{img_url}"
                state[key] = point["id"]
        if next_offset is None:
            break
        offset = next_offset
    print(f"✅ Found {len(state)} existing records in DB.")
    return state


async def run_visual_sync(user_id: str, job_id: int, db_factory):
    print(f"🚀 [Visual Agent] Starting Smart Sync Job {job_id} for User: {user_id}")
    try:
        # Pre-load CLIP model
        print("⏳ Pre-loading CLIP model...")
        get_visual_model()
        print("✅ CLIP model pre-loaded successfully.")

        await update_job_safe(db_factory, job_id, "processing")

        async with db_factory() as db:
            stmt = select(UserIntegration).where(
                UserIntegration.user_id == str(user_id),
                UserIntegration.is_active == True
            )
            result = await db.execute(stmt)
            integrations = result.scalars().all()

            # 🔥 Fetch user's selected vector DB
            user_result = await db.execute(select(User).where(User.id == int(user_id)))
            current_user = user_result.scalars().first()
            selected_provider = current_user.selected_vector_provider if current_user else ""
            selected_collection = current_user.selected_collection_name if current_user else ""

        vector_db_config = None
        store_config = None
        store_provider = None

        for i in integrations:
            # 🔥 Sirf selected provider ka vector DB use karein
            if i.provider == selected_provider:
                creds = json.loads(i.credentials)
                creds['provider'] = i.provider
                if selected_collection:
                    creds['visual_collection_name'] = selected_collection
                vector_db_config = creds
            elif i.provider in ['sanity', 'shopify', 'woocommerce', 'mongodb_store']:
                store_config = json.loads(i.credentials)
                store_provider = i.provider

        if not vector_db_config or not store_config:
            await update_job_safe(db_factory, job_id, "failed", error="Missing Database or Store connection.")
            return

        vector_store = get_visual_vector_store(credentials=vector_db_config)
        collection_name = vector_db_config.get("visual_collection_name", "visual_search_products")

        if not await vector_store.collection_exists(collection_name):
            print(f"🛠️ Creating new collection: {collection_name}")
            await vector_store.create_collection(
                collection_name=collection_name,
                vector_size=VECTOR_SIZE,
                distance="cosine"
            )

        source_products = await fetch_products_from_source(store_provider, store_config)
        if not source_products:
            await update_job_safe(db_factory, job_id, "completed", error="No products found in store.")
            return

        total_products = len(set([p['product_id'] for p in source_products]))
        total_images = len(source_products)

        db_state = await get_current_db_state(vector_store, collection_name, user_id)

        points_to_delete = []
        items_to_process = []
        source_keys = set()

        for prod in source_products:
            prod_id = prod.get('product_id')
            img_url = prod.get('image_url')
            if not prod_id or not img_url:
                continue
            key = f"{prod_id}::{img_url}"
            source_keys.add(key)
            if key in db_state:
                continue
            else:
                items_to_process.append(prod)

        for db_key, db_uuid in db_state.items():
            if db_key not in source_keys:
                points_to_delete.append(db_uuid)

        to_add_count = len(items_to_process)
        to_delete_count = len(points_to_delete)
        unchanged_count = total_images - to_add_count

        print(f"📊 Sync Analysis for User {user_id}:")
        print(f"   - Collection: {collection_name}")
        print(f"   - Total Products: {total_products}")
        print(f"   - Total Images: {total_images}")
        print(f"   - Unchanged (Skipping): {unchanged_count}")
        print(f"   - To Add/Update: {to_add_count}")
        print(f"   - To Delete (Removed from Store): {to_delete_count}")

        if points_to_delete:
            print(f"🗑️ Deleting {to_delete_count} obsolete records...")
            chunk_size = 1000
            for i in range(0, len(points_to_delete), chunk_size):
                chunk = points_to_delete[i:i + chunk_size]
                await vector_store.delete(collection_name=collection_name, ids=chunk)

        if items_to_process:
            print(f"⚡ Processing {to_add_count} new images...")
            processed_count = 0
            await update_job_safe(db_factory, job_id, "processing", processed=0, total=total_products, message=f"Processing images: 0/{to_add_count}")
            loop = asyncio.get_running_loop()

            for i in range(0, len(items_to_process), BATCH_SIZE):
                batch = items_to_process[i:i + BATCH_SIZE]
                points = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = [
                        loop.run_in_executor(executor, download_and_vectorize, item)
                        for item in batch
                    ]
                    results = await asyncio.gather(*futures)

                for res in results:
                    if res:
                        prod = res['product']
                        img_url = prod.get('image_url')
                        points.append({
                            "id": str(uuid4()),
                            "vector": res['vector'],
                            "payload": {
                                "product_id": prod.get('product_id'),
                                "slug": prod.get('slug'),
                                "image_url": img_url,
                                "title": prod.get('title', ''),
                                "price": prod.get('price'),
                                "user_id": str(user_id),
                                "source": store_provider
                            }
                        })

                if points:
                    await vector_store.upsert(collection_name=collection_name, points=points)
                    processed_count += len(points)

                await update_job_safe(db_factory, job_id, "processing", processed=processed_count, total=total_products, message=f"Processing images: {processed_count}/{to_add_count}")
                print(f"   -> Batch {i // BATCH_SIZE + 1} done. ({processed_count}/{to_add_count})")
        else:
            print("✨ No new images to process.")

        final_msg = f"Sync Complete. Products: {total_products}, Images: {to_add_count}, Deleted: {to_delete_count}"
        details = {"total_products": total_products, "total_images": total_images, "processed_images": to_add_count}
        await update_job_safe(db_factory, job_id, "completed", processed=to_add_count, total=total_products, message=final_msg, details=details)
        print(f"🎉 {final_msg}")

    except Exception as e:
        print(f"❌ Job {job_id} Failed: {e}")
        await update_job_safe(db_factory, job_id, "failed", error=str(e))