# Development Guidelines

## Project Overview
MealDB RAG System - A fast Retrieval-Augmented Generation system for recipe search using TheMealDB API with local caching and SQLite FTS5 indexing.

## Key Commands

### Initial Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Build Index
```bash
python -m src.cli init
```

### Query System
```bash
# Basic search
python -m src.cli ask "How to make pasta?"

# With SQL mode (requires API key)
python -m src.cli ask --use-toolfront-sql "List Mexican dishes"
```

## Testing Strategy
- Run `python -m pytest tests/` for unit tests
- Test data fetching with `python -m src.cli init`
- Verify search with sample queries
- Check cache efficiency on repeated runs

## Code Style Guidelines
- Use type hints for all function parameters and returns
- Follow PEP 8 conventions
- Keep functions focused and under 30 lines
- Document complex logic with inline comments
- Use descriptive variable names

## Architecture Notes

### Core Components
1. **Cache Layer** (`src/cache.py`)
   - File-based caching with expiry
   - Reduces API calls to TheMealDB

2. **Database** (`src/db.py`)
   - SQLite with FTS5 for fast search
   - Separate tables for meals and ingredients
   - Standalone FTS table for flexibility

3. **API Client** (`src/mealdb_api.py`)
   - Async fetching with rate limiting
   - Fetches by first letter (a-z, 0-9)

4. **RAG Engine** (`src/rag.py`)
   - Retrieval using FTS5 BM25 scoring
   - Optional ToolFront SQL integration
   - Context-based answer generation

## Common Issues & Solutions

### FTS5 UPSERT Error
- **Issue**: SQLite FTS5 doesn't support UPSERT
- **Solution**: Use DELETE then INSERT pattern

### Missing sqlite3-fts Package
- **Issue**: No such package exists
- **Solution**: FTS5 is built into SQLite, remove from requirements

### Environment Variables Not Loading
- **Issue**: .env not being read
- **Solution**: Add `load_dotenv()` to config.py

### API Quota Exceeded
- **Issue**: OpenAI quota limit reached
- **Solution**: Use different API key or model provider

## Performance Optimization
- Cache API responses (24hr default)
- Use FTS5 for O(log n) search
- Batch database operations
- Async API calls with throttling

## Security Considerations
- Never commit .env files
- Use .gitignore for sensitive data
- Validate all user inputs for SQL
- Sanitize FTS5 queries

## Future Enhancements
- Add more recipe sources
- Implement semantic search
- Add nutritional analysis
- Create web interface
- Support multi-language queries
- Add meal planning features