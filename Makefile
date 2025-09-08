.PHONY: help install init clean test demo

help:
	@echo "MealDB RAG System"
	@echo "================"
	@echo ""
	@echo "Available commands:"
	@echo "  install    - Set up virtual environment and install dependencies"
	@echo "  init       - Build the local index (fetch data from TheMealDB)"
	@echo "  demo       - Run example queries"
	@echo "  clean      - Clean cache and data files"
	@echo "  test       - Run basic tests"

install:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Installation complete. Edit .env if needed, then run 'make init'"

init:
	.venv/bin/python -m src.cli init
	@echo "✅ Index built successfully"

demo:
	@echo "🚀 Running basic demo..."
	.venv/bin/python -m src.cli ask "Italian pasta with tomatoes and garlic"
	@echo ""
	@echo "🚀 Running advanced examples..."
	.venv/bin/python examples/toolfront_example.py

clean:
	rm -rf cache/ data/ logs/
	@echo "✅ Cleaned cache, data, and logs"

test:
	@echo "🧪 Running basic functionality test..."
	.venv/bin/python -c "import sys; sys.path.append('src'); from rag import retrieve; print('✅ Basic import test passed')"
	@if [ -f "data/meals.db" ]; then \
		echo "✅ Database exists"; \
		.venv/bin/python -c "import sys; sys.path.append('src'); from rag import retrieve; print('Found {} meals'.format(len(retrieve('pasta', k=3))))"; \
	else \
		echo "⚠️  Database not found. Run 'make init' first"; \
	fi
