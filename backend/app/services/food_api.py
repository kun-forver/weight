"""Open Food Facts API service for searching and fetching food products."""

import logging
from typing import Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert any value to float."""
    if val is None:
        return default
    try:
        res = float(val)
        return res if res >= 0 else default
    except (ValueError, TypeError):
        return default


class OpenFoodFactsService:
    """Service for interacting with the Open Food Facts API."""

    def __init__(self) -> None:
        self.base_url = settings.OFF_API_URL
        self.timeout = 2.0
        self.headers = {"User-Agent": "FatLossPK/1.0 (contact@example.com)"}

    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search for food products on Open Food Facts.

        Returns a list of dicts with keys:
            name, calories (per 100g), protein, carbs, fat
        """
        if not query or not query.strip():
            return []

        params = {
            "search_terms": query.strip(),
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 20,
        }
        url = f"{self.base_url}/cgi/search.pl"
        results = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            for product in data.get("products", []):
                nutriments = product.get("nutriments", {})
                name = product.get("product_name") or product.get("generic_name") or ""
                if not name or not name.strip():
                    continue
                calories = (
                    nutriments.get("energy-kcal_100g")
                    or nutriments.get("energy-kcal")
                    or 0
                )
                protein = nutriments.get("proteins_100g") or 0
                carbs = nutriments.get("carbohydrates_100g") or 0
                fat = nutriments.get("fat_100g") or 0
                results.append(
                    {
                        "name": name.strip(),
                        "calories": safe_float(calories),
                        "protein": safe_float(protein),
                        "carbs": safe_float(carbs),
                        "fat": safe_float(fat),
                        "source": "openfoodfacts",
                    }
                )
        except Exception as e:
            logger.warning(f"OpenFoodFacts search error: {e}")
            return []
        return results

    async def get_by_barcode(self, barcode: str) -> dict[str, Any] | None:
        """Fetch a single product by its barcode from Open Food Facts."""
        if not barcode or not barcode.strip():
            return None
        url = f"{self.base_url}/api/v0/product/{barcode.strip()}.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            product = data.get("product")
            if not product:
                return None

            nutriments = product.get("nutriments", {})
            name = product.get("product_name") or product.get("generic_name") or ""
            if not name or not name.strip():
                return None

            calories = (
                nutriments.get("energy-kcal_100g")
                or nutriments.get("energy-kcal")
                or 0
            )
            return {
                "name": name.strip(),
                "barcode": barcode.strip(),
                "calories": safe_float(calories),
                "protein": safe_float(nutriments.get("proteins_100g")),
                "carbs": safe_float(nutriments.get("carbohydrates_100g")),
                "fat": safe_float(nutriments.get("fat_100g")),
                "source": "openfoodfacts",
            }
        except Exception as e:
            logger.warning(f"OpenFoodFacts barcode lookup error: {e}")
            return None


off_service = OpenFoodFactsService()

