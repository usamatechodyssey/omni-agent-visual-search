import shopify
import time
from typing import List, Dict, Any
from backend.src.modules.visual_search.services.connectors.base import BaseConnector


class ShopifyConnector(BaseConnector):
    """Shopify store se products aur images fetch karta hai (BaseConnector interface)."""

    def __init__(self, credentials: Dict[str, str]):
        self.shop_url = credentials.get("shop_url")
        self.access_token = credentials.get("access_token")
        self.api_version = credentials.get("api_version", "2024-01")

        if not self.shop_url or not self.access_token:
            raise ValueError("Shopify credentials (shop_url, access_token) are required.")

        self.session = shopify.Session(self.shop_url, self.api_version, self.access_token)

    def connect(self) -> bool:
        """Validate credentials by fetching a single product."""
        try:
            shopify.ShopifyResource.activate_session(self.session)
            # Fetch first product to test connection
            shopify.Product.find(limit=1)
            return True
        except Exception as e:
            print(f"❌ [ShopifyConnector] Connection failed: {e}")
            return False
        finally:
            shopify.ShopifyResource.clear_session()

    def fetch_products(self) -> List[Dict[str, Any]]:
        """Fetch all products with their image URLs."""
        print(f"🛍️ [ShopifyConnector] Connecting to {self.shop_url}...")
        shopify.ShopifyResource.activate_session(self.session)

        products = []
        try:
            page = shopify.Product.find(limit=250)

            while page:
                for product in page:
                    if not product.images:
                        continue
                    for image in product.images:
                        products.append({
                            "product_id": str(product.id),
                            "slug": product.handle,
                            "image_url": image.src,
                            "title": product.title,
                            "price": product.variants[0].price if product.variants else None,
                            "source": "shopify"
                        })

                if page.has_next_page():
                    time.sleep(0.5)  # Rate limiting
                    page = page.next_page()
                else:
                    break

            print(f"✅ [ShopifyConnector] Fetched {len(products)} images successfully.")
            return products
        except Exception as e:
            print(f"❌ [ShopifyConnector] Error fetching products: {e}")
            return []
        finally:
            shopify.ShopifyResource.clear_session()

    def get_schema_summary(self) -> str:
        """Return standard Shopify data structure description."""
        return "Shopify store with fields: product_id, slug, image_url, title, price, source."