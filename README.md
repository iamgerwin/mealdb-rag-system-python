# MealDB RAG (with local cache + ToolFront)

Simple, fast Retrieval-Augmented Generation over TheMealDB using a local SQLite FTS index and optional ToolFront integration.

Features
- Caches API responses on disk to speed up repeated runs
- Builds a local SQLite database with FTS5 for instant retrieval
- Exposes a simple CLI for indexing and asking questions
- Optional: use ToolFront's Database.ask (Text2SQL) to answer questions with SQL over the local DB

Prerequisites
- Python 3.10+
- Internet access for initial data fetch from TheMealDB

Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit if needed
```

Usage
1) Build the local index (cached + SQLite):
```
python -m src.cli init
```
2) Ask a question (returns a synthesized answer prompt + top contexts):
```
python -m src.cli ask "How do I make a classic Italian pasta with tomatoes?"
```
3) Ask using ToolFront's Text2SQL over the local DB (requires a model key, e.g., OPENAI_API_KEY):
```
export OPENAI_API_KEY=...  # or ANTHROPIC_API_KEY, etc.
python -m src.cli ask --use-toolfront-sql true "List a few Mexican chicken meals by name"
```

How it works
- Data fetch: pulls meals from TheMealDB free API by first letter (a-z, 0-9). Responses are cached in ./cache.
- Indexing: stores meals in ./data/meals.db, and creates an FTS5 virtual table for fast keyword/natural-language-like search.
- Retrieval: queries FTS with your question and returns the top-k meals' instructions as context.
- Generation: by default, prints a synthesized prompt you can paste into your model. If --use-toolfront-sql is enabled and ToolFront is installed (requirements.txt), it calls Database.ask to produce a structured answer, and appends the top supporting contexts.

Notes
- TheMealDB test key "1" is used by default. For production-scale needs (full dumps, latest meals, multi-ingredient filters), consider becoming a supporter and upgrading the API key.
- You can re-run `init` anytime; cached responses keep it fast. To refresh, delete ./cache or increase CACHE_EXPIRY_HOURS in .env.
- This project intentionally avoids storing any API secrets in code. Use environment variables.

Project layout
- src/config.py: settings and paths
- src/logger.py: log configuration
- src/cache.py: simple file cache for API responses
- src/mealdb_api.py: async client for TheMealDB
- src/db.py: SQLite schema (with FTS5), upserts, and search
- src/indexer.py: end-to-end dataset fetch + index build
- src/rag.py: retrieval and answer composition; optional ToolFront Text2SQL
- src/cli.py: Typer CLI with `init` and `ask`
- examples/: quickstart script and usage example
- docs/: reserved for extended docs

Example programmatic use
```
from src.rag import answer
print(answer("What is a simple Canadian dessert and how to make it?", k=3))
```

Troubleshooting
- If FTS5 is unavailable in your Python's SQLite build, install a recent Python or use Homebrew Python on macOS.
- If ToolFront SQL mode errors, ensure you exported a valid model key (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.) and your network allows outbound calls.

Contributing
------------
We welcome contributions! Here's how to get started:

1. **Reporting Issues**
   - Check existing issues first
   - Provide detailed reproduction steps and expected behavior

2. **Pull Requests**
   - Fork the repository and create a feature branch
   - Include tests for new functionality
   - Update documentation if needed
   - Keep commits atomic and messages clear

3. **Code Style**
   - Follow existing patterns in the codebase
   - Use type hints where applicable
   - Keep functions small and focused

4. **Testing**
   - Run `make test` before submitting PRs
   - Add unit tests for new features
   - Include integration tests for complex interactions
