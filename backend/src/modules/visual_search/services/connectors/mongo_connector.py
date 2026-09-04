# backend/src/modules/visual_search/services/connectors/mongo_connector.py

import pymongo
from typing import List, Dict, Any, Optional
from backend.src.modules.visual_search.services.connectors.base import BaseConnector


class MongoProductConnector(BaseConnector):
    """
    User ke existing MongoDB database se products fetch karta hai.
    User apna data pattern explain karega (field_mapping + image_mode).
    """

    def __init__(self, credentials: Dict[str, str]):
        self.connection_string = credentials.get("connection_string") or credentials.get("url")
        self.database_name = credentials.get("database_name", "products")
        self.collection_name = credentials.get("collection_name", "products")
        self.field_mapping = credentials.get("field_mapping", {})

        # Image Adapter/Mode (e.g., "cdn", "local", "mixed")
        self.image_mode = credentials.get("image_mode", "mixed")

        # 🔧 IMPROVEMENT: tls_insecure ab hardcoded nahi, per-customer
        # credentials se configurable hai. Default False — jab IP whitelist
        # sahi ho to cert validation on rakhna zyada secure hai. Agar kisi
        # customer ka apna Mongo self-signed cert use karta ho, tou wo
        # credentials mein "tls_insecure": True bhej sakta hai.
        self.tls_insecure = credentials.get("tls_insecure", False)

        if not self.connection_string:
            raise ValueError("MongoDB connection string is required.")

        self.client: Optional[pymongo.MongoClient] = None
        self.db = None
        self.collection = None
        self.last_error: Optional[str] = None  # 🔧 NEW: job "details" mein error dikhane ke liye

    def connect(self) -> bool:
        """Connect to MongoDB and validate collection exists."""
        try:
            client_kwargs = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 20000,
                "socketTimeoutMS": 20000,
                "tls": True,
            }
            if self.tls_insecure:
                client_kwargs["tlsInsecure"] = True

            self.client = pymongo.MongoClient(self.connection_string, **client_kwargs)
            self.client.server_info()
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ [MongoConnector] Connection failed: {e}")
            return False

    def close(self) -> None:
        """🔧 NEW: connection ko explicitly band karta hai — har fetch ke baad
        client khula chhod dena, baar baar sync jobs chalne par connection
        leak ban sakta tha."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None

    def _get_field(self, item: dict, field_name: str, default: str = ""):
        """User ke field_mapping ke hisaab se value nikalein (nested dot path support)."""
        path = self.field_mapping.get(field_name, default)

        if not path:
            path = field_name if field_name in item else None

        if not path:
            return ""

        value = item
        for part in path.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return ""
        return value

    def _get_all_images(self, item: dict) -> List[str]:
        """
        Multi-Adapter Image Extractor:
        `image_mode` ke hisaab se images extract karta hai.
        """
        mode = self.image_mode.lower()
        final_urls = []

        def extract_from_path(path: str):
            if not path:
                return []

            parts = path.split('.')
            current = item
            urls = []

            for part in parts[:-1]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    new_current = []
                    for el in current:
                        if isinstance(el, dict) and part in el:
                            new_current.append(el[part])
                    current = new_current
                else:
                    return []

            if isinstance(current, list):
                for el in current:
                    if isinstance(el, dict) and parts[-1] in el:
                        urls.append(el[parts[-1]])
                    elif isinstance(el, str):
                        urls.append(el)
                    elif isinstance(el, list):
                        for sub_el in el:
                            if isinstance(sub_el, dict) and parts[-1] in sub_el:
                                urls.append(sub_el[parts[-1]])
                            elif isinstance(sub_el, str):
                                urls.append(sub_el)
            elif isinstance(current, str):
                urls.append(current)

            return [u for u in urls if u]

        if mode == "cdn":
            path = self.field_mapping.get("image_url", "variants.cdnImages.url")
            final_urls.extend(extract_from_path(path))

        elif mode == "local":
            path = self.field_mapping.get("image_url", "variants.images.url")
            final_urls.extend(extract_from_path(path))

        else:  # Mixed (default)
            cdn_path = self.field_mapping.get("cdn_image_url", "variants.cdnImages.url")
            local_path = self.field_mapping.get("local_image_url", "variants.images.url")

            urls = extract_from_path(cdn_path) + extract_from_path(local_path)
            final_urls = list(dict.fromkeys(urls))

        return final_urls

    def fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch all products using field_mapping. Har image ki alag entry banayega."""
        if not self.connect():
            return []

        try:
            products = []
            cursor = self.collection.find({}).limit(10000)

            for doc in cursor:
                product_id = self._get_field(doc, "product_id", "_id")
                slug = self._get_field(doc, "slug", "slug")
                title = self._get_field(doc, "title", "name")
                price = self._get_field(doc, "price", None)

                image_urls = self._get_all_images(doc)

                if not product_id or not image_urls:
                    continue

                for img_url in image_urls:
                    if not img_url:
                        continue

                    products.append({
                        "product_id": str(product_id),
                        "slug": slug or str(product_id),
                        "image_url": img_url,
                        "title": title,
                        "price": price,
                        "source": "mongodb_store"
                    })

            return products
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ [MongoConnector] Fetch failed: {e}")
            return []
        finally:
            self.close()  # 🔧 NEW: success ho ya fail, connection hamesha band karo

    def get_schema_summary(self) -> str:
        """Return collection field names for user reference."""
        if not self.connect():
            return f"MongoDB connection failed: {self.last_error}"

        try:
            sample = self.collection.find_one()
            if sample:
                fields = list(sample.keys())
                return f"MongoDB Collection '{self.collection_name}' has fields: {fields}"
            return f"MongoDB Collection '{self.collection_name}' is empty."
        except Exception as e:
            return f"MongoDB error: {e}"
        finally:
            self.close()