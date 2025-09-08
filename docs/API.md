# API Reference

## Core Functions

### `retrieve(question: str, k: int = 5) -> List[Dict]`

Retrieves the top-k most relevant meals from the local index using FTS search.

**Parameters:**
- `question`: Natural language query or keywords
- `k`: Number of results to return (default: 5)

**Returns:** List of meal dictionaries with fields: id, name, category, area, tags, instructions, thumbnail

**Example:**
```python
from src.rag import retrieve
results = retrieve("Italian pasta with tomatoes", k=3)
for meal in results:
    print(f"{meal['name']} - {meal['category']}")
```

### `answer(question: str, k: int = 5, use_toolfront_sql: bool = False, model: str = None) -> str`

Generates an answer using retrieved contexts, with optional ToolFront Text2SQL integration.

**Parameters:**
- `question`: Your question in natural language
- `k`: Number of contexts to retrieve (default: 5) 
- `use_toolfront_sql`: Whether to use ToolFront's Database.ask for structured SQL queries (default: False)
- `model`: AI model to use, e.g., "openai:gpt-4o", "anthropic:claude-3-5-sonnet" (default: from config)

**Returns:** String containing either a prompt with contexts (default) or a structured answer (when using ToolFront)

**Example:**
```python
from src.rag import answer

# Basic prompt generation
prompt = answer("How do I cook seafood pasta?")
print(prompt)

# With ToolFront (requires API key)
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
structured_answer = answer("List Mexican chicken meals", use_toolfront_sql=True)
print(structured_answer)
```

## Database Schema

### Tables

**meals**
- `id` (INTEGER PRIMARY KEY): Meal ID from TheMealDB
- `name` (TEXT): Meal name
- `category` (TEXT): Category (e.g., "Pasta", "Chicken")
- `area` (TEXT): Cuisine area (e.g., "Italian", "Mexican")
- `instructions` (TEXT): Cooking instructions
- `thumbnail` (TEXT): URL to meal image
- `tags` (TEXT): Comma-separated tags

**meal_ingredients** 
- `meal_id` (INTEGER): Foreign key to meals.id
- `ingredient` (TEXT): Ingredient name
- `measure` (TEXT): Amount/measurement

**meals_fts** (Virtual FTS5 Table)
- Full-text search index over name, instructions, tags, category, area, and ingredients

## CLI Commands

### `python -m src.cli init`
Fetches all data from TheMealDB and builds the local index.

### `python -m src.cli ask <question>`
Asks a question and returns contexts/answer.

**Options:**
- `--k INTEGER`: Number of contexts to retrieve (default: 5)
- `--use-toolfront-sql`: Use ToolFront Text2SQL mode
- `--model TEXT`: Override default AI model

## Configuration

Set environment variables in `.env`:

- `THEMEALDB_API_KEY`: API key (default: "1" for testing)
- `THEMEALDB_BASE_URL`: Base API URL
- `DEFAULT_MODEL`: Default AI model for ToolFront
- `CACHE_DIR`: Cache directory path  
- `CACHE_EXPIRY_HOURS`: Cache TTL in hours
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

The system gracefully handles:
- Network timeouts during data fetching
- Missing/corrupt cache files
- SQLite FTS syntax errors
- ToolFront API failures (falls back to prompt generation)

Errors are logged to `./logs/mealdb-rag.log` and console.
