#!/usr/bin/env python3
"""
Advanced example showing ToolFront integration with the MealDB RAG system.

This example demonstrates:
1. Basic retrieval without AI model
2. Using ToolFront's Database.ask for structured SQL queries
3. Combining both approaches for comprehensive answers
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Allow running directly
sys.path.append(str((Path(__file__).resolve().parent.parent / 'src').resolve()))

from rag import answer, retrieve
from config import settings

def demo_basic_retrieval():
    print("=== Basic Retrieval (No AI Model) ===")
    question = "Italian pasta with tomatoes"
    contexts = retrieve(question, k=3)
    
    print(f"Question: {question}")
    print(f"Found {len(contexts)} relevant meals:")
    for ctx in contexts:
        print(f"- {ctx['name']} ({ctx['category']}, {ctx['area']})")
    print()

def demo_rag_prompt():
    print("=== RAG Prompt Generation ===")
    question = "How do I make a seafood pasta dish?"
    response = answer(question, k=2, use_toolfront_sql=False)
    print(response[:500] + "..." if len(response) > 500 else response)
    print()

def demo_toolfront_sql():
    print("=== ToolFront Text2SQL (requires API key) ===")
    
    # Check if we have model API key
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    
    if not (has_openai or has_anthropic or has_google):
        print("⚠️  No AI model API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY to try this feature.")
        return
    
    try:
        question = "What are the names of Mexican chicken dishes in the database?"
        response = answer(question, k=3, use_toolfront_sql=True)
        print(f"Question: {question}")
        print(response)
    except Exception as e:
        print(f"Error with ToolFront: {e}")
        print("Make sure ToolFront is installed and your API key is valid.")
    print()

def main():
    print("MealDB RAG System - Advanced Examples")
    print("=" * 50)
    
    # Check if index exists
    db_path = settings.data_dir / "meals.db"
    if not db_path.exists():
        print("❌ Database not found. Please run 'python -m src.cli init' first.")
        return
    
    demo_basic_retrieval()
    demo_rag_prompt()
    demo_toolfront_sql()
    
    print("Examples completed! 🎉")

if __name__ == "__main__":
    main()
