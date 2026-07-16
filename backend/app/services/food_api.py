"""Open Food Facts API service for searching and fetching food products."""

import httpx
from typing import Any

from app.config import settings


class OpenFoodFactsService:
    """Service for interacting with the Open Food Facts API."""

    def __init__(self) -> None:
        self.base_url = settings.OFF_API_URL
        self.timeout = 1.5


    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search for food products on Open Food Facts.

        Returns a list of dicts with keys:
            name, calories (per 100g), protein, carbs, fat
        """
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 20,
        }
        url = f"{self.base_url}/cgi/search.pl"
        results = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            for product in data.get("products", []):
                nutriments = product.get("nutriments", {})
                name = product.get("product_name") or product.get("generic_name") or ""
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
                        "name": name,
                        "calories": float(calories) if calories else 0,
                        "protein": float(protein) if protein else 0,
                        "carbs": float(carbs) if carbs else 0,
                        "fat": float(fat) if fat else 0,
                        "source": "openfoodfacts",
                    }
                )
        except (httpx.HTTPError, KeyError, ValueError) as e:
            # In production, log the error
            print(f"OpenFoodFacts search error: {e}")
            return []
        return results

    async def get_by_barcode(self, barcode: str) -> dict[str, Any] | None:
        """Fetch a single product by its barcode from Open Food Facts.

        Returns a dict with keys:
            name, calories (per 100g), protein, carbs, fat, barcode
        """
        url = f"{self.base_url}/api/v0/product/{barcode}.json"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            product = data.get("product")
            if not product:
                return None

            nutriments = product.get("nutriments", {})
            name = product.get("product_name") or product.get("generic_name") or ""
            calories = (
                nutriments.get("energy-kcal_100g")
                or nutriments.get("energy-kcal")
                or 0
            )
            return {
                "name": name,
                "barcode": barcode,
                "calories": float(calories) if calories else 0,
                "protein": float(nutriments.get("proteins_100g") or 0),
                "carbs": float(nutriments.get("carbohydrates_100g") or 0),
                "fat": float(nutriments.get("fat_100g") or 0),
                "source": "openfoodfacts",
            }
        except (httpx.HTTPError, KeyError, ValueError) as e:
            print(f"OpenFoodFacts barcode lookup error: {e}")
            return None


off_service = OpenFoodFactsService()
