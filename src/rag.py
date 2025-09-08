from __future__ import annotations
from typing import List, Dict

from .db import search_meals
from .logger import logger
from .config import settings

try:
    from toolfront import Database  # Optional: use ToolFront Text2SQL for advanced queries
    _TOOLFRONT_AVAILABLE = True
except Exception:
    _TOOLFRONT_AVAILABLE = False


def retrieve(question: str, k: int = 5) -> List[Dict]:
    # Use a simple FTS query; allow natural language by quoting terms with OR
    # For simplicity, we pass the raw question to MATCH; users can also specify FTS syntax
    rows = search_meals(question, limit=k)
    contexts = []
    for r in rows:
        ingredients_preview = ""  # Could join from meal_ingredients if needed
        contexts.append(
            {
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "area": r["area"],
                "tags": r["tags"],
                "instructions": r["instructions"],
                "thumbnail": r["thumbnail"],
            }
        )
    return contexts


def make_context_block(contexts: List[Dict]) -> str:
    blocks = []
    for c in contexts:
        block = (
            f"Meal: {c['name']} (#{c['id']})\n"
            f"Category: {c.get('category')}, Area: {c.get('area')}, Tags: {c.get('tags')}\n"
            f"Instructions:\n{c.get('instructions')}\n"
        )
        blocks.append(block)
    return "\n---\n".join(blocks)


def answer(question: str, k: int = 5, use_toolfront_sql: bool = False, model: str | None = None) -> str:
    model = model or settings.default_model

    # Retrieve contexts
    contexts = retrieve(question, k=k)
    if not contexts:
        return "No relevant meals found. Try different keywords."

    context_block = make_context_block(contexts)

    # If ToolFront Database is available and requested, let it formulate SQL to fetch structured answers
    if use_toolfront_sql and _TOOLFRONT_AVAILABLE:
        try:
            db = Database(f"sqlite:///{(settings.data_dir / 'meals.db').resolve()}")
            tf_answer = db.ask(
                f"Using meals and meal_ingredients tables, answer: {question}. If relevant, include meal names.",
                model=model,
                context="The database contains tables: meals(id, name, category, area, instructions, thumbnail, tags) and meal_ingredients(meal_id, ingredient, measure).",
            )
            # Combine structured answer with retrieved context
            return (
                "Answer (ToolFront Text2SQL):\n" + str(tf_answer) +
                "\n\nTop supporting context:\n" + context_block
            )
        except Exception as e:
            logger.warning(f"ToolFront Database.ask failed, falling back to context-only response: {e}")

    # Default: return a concise synthesized response prompt for the model consumer
    synthesized = (
        "Question: " + question +
        "\n\nTop retrieved meal context (use to answer):\n" + context_block +
        "\n\nProvide a concise answer using the context above."
    )
    # We don't invoke a model directly; ToolFront can be used by the caller if desired.
    return synthesized
