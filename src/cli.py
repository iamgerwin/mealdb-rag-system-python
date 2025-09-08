from __future__ import annotations
import asyncio
from typing import Optional

import typer
from rich import print
from rich.panel import Panel

from .indexer import build_index
from .rag import answer
from .config import settings
from .logger import logger

app = typer.Typer(help="MealDB RAG: build local index and answer questions quickly with cached data.")


@app.command()
def init():
    """Fetch all MealDB data and build the local index (cached + SQLite FTS)."""
    asyncio.run(build_index())
    print(Panel.fit("[green]Index built successfully[/green]"))


@app.command()
def ask(question: str = typer.Argument(..., help="Your question in natural language"),
        k: int = typer.Option(5, help="Number of contexts to retrieve"),
        use_toolfront_sql: bool = typer.Option(False, help="Use ToolFront Text2SQL over SQLite for the answer"),
        model: Optional[str] = typer.Option(None, help="Override default model, e.g., 'openai:gpt-4o'")):
    """Ask a question. By default returns a synthesized prompt with top contexts; optionally use ToolFront."""
    resp = answer(question, k=k, use_toolfront_sql=use_toolfront_sql, model=model)
    print(resp)


if __name__ == "__main__":
    app()
