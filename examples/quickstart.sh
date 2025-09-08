#!/usr/bin/env bash
set -euo pipefail

# Quickstart for MealDB RAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: set model provider keys if you plan to use ToolFront with a model
# export OPENAI_API_KEY=...  # or ANTHROPIC_API_KEY=..., etc.

python -m src.cli init
python -m src.cli ask "Give me a seafood dinner idea with step-by-step instructions"
