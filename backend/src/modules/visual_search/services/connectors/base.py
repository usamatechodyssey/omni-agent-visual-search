from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseConnector(ABC):
    """
    Common interface for all product connectors.
    Any new connector (Shopify, WooCommerce, MongoDB, Sanity, etc.) must implement these methods.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Test connection and validate credentials."""
        pass

    @abstractmethod
    def fetch_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products with their image URLs.
        Each product must have:
        - product_id: str
        - slug: str
        - image_url: str
        """
        pass

    @abstractmethod
    def get_schema_summary(self) -> str:
        """Return a string description of the data structure (for LLM/UI)."""
        pass