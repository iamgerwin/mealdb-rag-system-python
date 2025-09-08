from __future__ import annotations
import asyncio
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp

from .config import settings
from .cache import cache
from .logger import logger


class MealDBClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.themealdb_base_url
        self.api_key = api_key or settings.themealdb_api_key

    def _url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        if params is None:
            params = {}
        qp = urlencode(params)
        url = f"{self.base_url}/{path}"
        if qp:
            url = f"{url}?{qp}"
        return url

    async def _get_json(self, session: aiohttp.ClientSession, path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = self._url(path, params)
        cached = cache.get(url)
        if cached is not None:
            return cached
        async with session.get(url, timeout=30) as resp:
            resp.raise_for_status()
            data = await resp.json()
            cache.set(url, data)
            return data

    async def search_by_first_letter(self, session: aiohttp.ClientSession, letter: str) -> List[Dict[str, Any]]:
        data = await self._get_json(session, "search.php", {"f": letter})
        return data.get("meals") or []

    async def lookup_by_id(self, session: aiohttp.ClientSession, meal_id: str | int) -> Optional[Dict[str, Any]]:
        data = await self._get_json(session, "lookup.php", {"i": str(meal_id)})
        meals = data.get("meals") or []
        return meals[0] if meals else None

    async def list_all_categories(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        data = await self._get_json(session, "categories.php")
        return data.get("categories") or []

    async def list_basic(self, session: aiohttp.ClientSession, kind: str) -> List[Dict[str, Any]]:
        # kind in {c: categories, a: areas, i: ingredients}
        data = await self._get_json(session, "list.php", {kind: "list"})
        return data.get("meals") or []

    async def fetch_all_meals(self) -> List[Dict[str, Any]]:
        letters = [chr(c) for c in range(ord('a'), ord('z')+1)] + [str(d) for d in range(0,10)]
        results: List[Dict[str, Any]] = []
        async with aiohttp.ClientSession() as session:
            for letter in letters:
                try:
                    meals = await self.search_by_first_letter(session, letter)
                    results.extend(meals)
                except Exception as e:
                    logger.warning(f"Failed fetching meals for letter {letter}: {e}")
        logger.info(f"Fetched {len(results)} meals (raw)")
        return results


async def dump_full_dataset_json(path: str) -> None:
    client = MealDBClient()
    meals = await client.fetch_all_meals()
    # Ensure unique by idMeal
    by_id: Dict[str, Dict[str, Any]] = {}
    for m in meals:
        mid = str(m.get("idMeal"))
        by_id[mid] = m
    data = sorted(by_id.values(), key=lambda x: int(x.get("idMeal", 0)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"meals": data}, f, ensure_ascii=False)
    logger.info(f"Saved {len(data)} unique meals to {path}")
