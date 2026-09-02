from woocommerce import API
from typing import List, Dict, Any
from backend.src.modules.visual_search.services.connectors.base import BaseConnector


class WooCommerceConnector(BaseConnector):
    """WooCommerce store se products aur images fetch karta hai (BaseConnector interface)."""

    def __init__(self, credentials: Dict[str, str]):
        self.url = credentials.get("website_url") or credentials.get("url")
        self.consumer_key = credentials.get("consumer_key")
        self.consumer_secret = credentials.get("consumer_secret")

        if not all([self.url, self.consumer_key, self.consumer_secret]):
            raise ValueError("WooCommerce credentials (url, consumer_key, consumer_secret) are required.")

        self.wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3",
            timeout=20
        )

    def connect(self) -> bool:
        """Validate credentials by fetching a single product."""
        try:
            response = self.wcapi.get("products", params={"per_page": 1})
            return response.status_code == 200
        except Exception as e:
            print(f"❌ [WooConnector] Connection failed: {e}")
            return False

    def fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch all products with their image URLs."""
        print(f"🛒 [WooConnector] Connecting to {self.url}...")

        products = []
        page = 1
        per_page = 50

        try:
            while True:
                response = self.wcapi.get("products", params={"per_page": per_page, "page": page, "status": "publish"})

                if response.status_code != 200:
                    print(f"⚠️ [WooConnector] Error on page {page}: {response.status_code}")
                    break

                data = response.json()
                if not data:
                    break

                for product in data:
                    if not product.get("images"):
                        continue
                    for image in product["images"]:
                        products.append({
                            "product_id": str(product["id"]),
                            "slug": product["slug"],
                            "image_url": image["src"],
                            "title": product["name"],
                            "price": product.get("price"),
                            "source": "woocommerce"
                        })

                page += 1

            print(f"✅ [WooConnector] Fetched {len(products)} images successfully.")
            return products
        except Exception as e:
            print(f"❌ [WooConnector] Connection Error: {e}")
            return []

    def get_schema_summary(self) -> str:
        """Return standard WooCommerce data structure description."""
        return "WooCommerce store with fields: product_id, slug, image_url, title, price, source."