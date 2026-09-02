import requests
import json
from urllib.parse import quote
from typing import List, Dict, Any
from backend.src.modules.visual_search.services.connectors.base import BaseConnector


class SanityConnector(BaseConnector):
    """Sanity CMS se products fetch karta hai (User ke custom GROQ Query aur Field Mapping ke saath)."""

    def __init__(self, credentials: Dict[str, str]):
        self.project_id = credentials.get("project_id")
        self.dataset = credentials.get("dataset")
        self.token = credentials.get("token")  # Read-only token
        self.api_version = credentials.get("api_version", "v2021-10-21")

        # --- CUSTOM QUERY & MAPPING (User Configurable) ---
        self.custom_query = credentials.get("custom_query")  # User apni GROQ query de sakta hai
        self.field_mapping = credentials.get("field_mapping", {})  # User field names set karega

        if not all([self.project_id, self.dataset, self.token]):
            raise ValueError("Sanity credentials (project_id, dataset, token) are required.")

        self.base_url = f"https://{self.project_id}.api.sanity.io/{self.api_version}/data/query/{self.dataset}"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.is_connected = False

    def connect(self) -> bool:
        """Test connection by fetching a simple query."""
        if self.is_connected:
            return True

        try:
            test_query = '*[_type == "sanity.imageAsset"][0...1]'
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"query": test_query},
                timeout=10
            )

            if response.status_code == 200:
                self.is_connected = True
                print(f"✅ [SanityConnector] Connected to Project: {self.project_id}")
                return True
            else:
                print(f"❌ [SanityConnector] Connection Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ [SanityConnector] Connection Error: {e}")
            return False

    def _get_field(self, item: dict, field_name: str, default: str = ""):
        """User ke field_mapping ke hisaab se value nikalein (nested paths support nahi, simple dot path)"""
        path = self.field_mapping.get(field_name, default)
        if not path:
            # Agar mapping nahi hai, to standard names try karein
            path = field_name if field_name in item else None
        
        if not path:
            return ""
        
        # Simple dot notation support: "variants[0].price" (bas kar rahe hain)
        value = item
        for part in path.split('.'):
            if part.startswith('[') and part.endswith(']'):
                try:
                    index = int(part[1:-1])
                    value = value[index] if isinstance(value, list) else value
                except:
                    return ""
            else:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return ""
        return value or ""

    def fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch products using User's custom query or default query, with field mapping."""
        if not self.connect():
            return []

        print(f"🕵️ [SanityConnector] Fetching products (Query: {'Custom' if self.custom_query else 'Default'})...")
        products = []

        try:
            # --- Query Selection Logic (User Custom ya Default) ---
            query = self.custom_query
            if not query:
                # Default query: Standard e-commerce with variants and images
                query = """*[_type == "product" && defined(variants)]{
                    _id, "slug": slug.current, "title": title,
                    "variants": variants[]{ _key, images[]{ asset->{url} } }
                }"""

            encoded_query = quote(query)
            response = requests.get(
                f"{self.base_url}?query={encoded_query}",
                headers=self.headers,
                timeout=15
            )

            if response.status_code != 200:
                print(f"❌ [SanityConnector] Query failed: {response.status_code}")
                return []

            raw_data = response.json().get("result", [])

            for item in raw_data:
                # **Use Field Mapping to extract data**
                # Agar user ne mapping nahi di, to standard Sanity paths use karo
                product_id = self._get_field(item, "product_id", "_id")
                slug = self._get_field(item, "slug", "slug")
                # Image URL field ko dhoondhna hai (nested ho sakta hai variants mein)
                image_url = self._get_field(item, "image_url", "url")
                
                # **Nested Variant Handling (Default Fallback)**
                if not image_url and item.get("variants"):
                    for variant in item["variants"]:
                        if variant.get("images"):
                            for img in variant["images"]:
                                if img.get("asset") and img["asset"].get("url"):
                                    image_url = img["asset"]["url"]
                                    break
                            if image_url:
                                break

                if not product_id or not image_url:
                    continue  # Skip products without images

                products.append({
                    "product_id": str(product_id),
                    "slug": self._get_field(item, "slug", "slug") or slug,
                    "image_url": image_url,
                    "title": self._get_field(item, "title", "title"),
                    "price": self._get_field(item, "price", None),  # User ke mapping se price nikaalein
                    "source": "sanity"
                })

            print(f"✅ [SanityConnector] Fetched {len(products)} images successfully.")
            return products

        except Exception as e:
            print(f"❌ [SanityConnector] Fetch error: {e}")
            return []

    def get_schema_summary(self) -> str:
        """Return Sanity data structure description (User can review in dashboard)."""
        return "Sanity CMS. User can configure custom GROQ query and field mappings for product_id, slug, image_url."