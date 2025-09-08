from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, Dict, Any, List

from .config import settings
from .logger import logger

DB_PATH = (settings.data_dir / "meals.db").resolve()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = connect()
    cur = conn.cursor()
    # Enable FTS5
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            area TEXT,
            instructions TEXT,
            thumbnail TEXT,
            tags TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS meals_fts USING fts5(
            name, instructions, tags, category, area, ingredients
        );

        CREATE TABLE IF NOT EXISTS meal_ingredients (
            meal_id INTEGER,
            ingredient TEXT,
            measure TEXT,
            PRIMARY KEY (meal_id, ingredient),
            FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()
    logger.info(f"Initialized DB at {DB_PATH}")


def upsert_meals(meals: Iterable[Dict[str, Any]]) -> int:
    conn = connect()
    cur = conn.cursor()
    count = 0
    for m in meals:
        try:
            meal_id = int(m.get("idMeal"))
            name = m.get("strMeal")
            category = m.get("strCategory")
            area = m.get("strArea")
            instructions = (m.get("strInstructions") or "").strip()
            thumbnail = m.get("strMealThumb")
            tags = m.get("strTags") or ""

            cur.execute(
                """
                INSERT INTO meals(id, name, category, area, instructions, thumbnail, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name=excluded.name,
                  category=excluded.category,
                  area=excluded.area,
                  instructions=excluded.instructions,
                  thumbnail=excluded.thumbnail,
                  tags=excluded.tags
                """,
                (meal_id, name, category, area, instructions, thumbnail, tags),
            )

            # Ingredients
            cur.execute("DELETE FROM meal_ingredients WHERE meal_id = ?", (meal_id,))
            ingredients: List[str] = []
            for i in range(1, 21):
                ing = (m.get(f"strIngredient{i}") or "").strip()
                meas = (m.get(f"strMeasure{i}") or "").strip()
                if ing:
                    cur.execute(
                        "INSERT OR REPLACE INTO meal_ingredients(meal_id, ingredient, measure) VALUES (?, ?, ?)",
                        (meal_id, ing, meas),
                    )
                    ingredients.append(ing)
            # Update FTS - FTS5 doesn't support UPSERT, so delete then insert
            ingredients_text = ", ".join(ingredients)
            cur.execute("DELETE FROM meals_fts WHERE rowid = ?", (meal_id,))
            cur.execute(
                "INSERT INTO meals_fts(rowid, name, instructions, tags, category, area, ingredients) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (meal_id, name, instructions, tags, category, area, ingredients_text),
            )
            count += 1
        except Exception as e:
            logger.warning(f"Failed upserting meal {m.get('idMeal')}: {e}")
    conn.commit()
    conn.close()
    logger.info(f"Upserted {count} meals")
    return count


def search_meals(query: str, limit: int = 5) -> List[sqlite3.Row]:
    conn = connect()
    cur = conn.cursor()
    try:
        # Escape special characters for FTS5 and convert to simple query
        # Remove special characters and use simple terms
        import re
        clean_query = re.sub(r'[^\w\s]', ' ', query)
        # Join words with OR for broader matching
        fts_query = ' OR '.join(clean_query.split())
        
        cur.execute(
            "SELECT m.*, bm25(meals_fts) as score FROM meals_fts JOIN meals m ON meals_fts.rowid = m.id WHERE meals_fts MATCH ? ORDER BY score LIMIT ?",
            (fts_query, limit),
        )
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()
