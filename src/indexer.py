from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

from .logger import logger
from .mealdb_api import dump_full_dataset_json
from .db import init_db, upsert_meals
from .config import settings


async def build_index(output_json: Path | None = None) -> None:
    if output_json is None:
        output_json = settings.data_dir / "meals.json"
    await dump_full_dataset_json(str(output_json))

    with open(output_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    meals: List[Dict[str, Any]] = data.get("meals") or []

    init_db()
    upsert_meals(meals)
    logger.info("Index build complete")
