#!/usr/bin/env python3
"""Basic tests for the MealDB RAG system."""
from __future__ import annotations
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Settings
from cache import FileCache
from db import init_db, upsert_meals, search_meals


def test_cache():
    """Test file cache functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(ttl_hours=1, base_dir=Path(tmpdir))
        
        # Test set/get
        cache.set("test_key", {"data": "test_value"})
        result = cache.get("test_key")
        assert result == {"data": "test_value"}
        
        # Test non-existent key
        result = cache.get("nonexistent")
        assert result is None
        
        print("✅ Cache tests passed")


def test_database():
    """Test database operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override settings for testing
        import config
        config.settings.data_dir = Path(tmpdir)
        
        # Initialize DB
        init_db()
        
        # Test data
        meals = [
            {
                "idMeal": "1",
                "strMeal": "Test Pasta",
                "strCategory": "Pasta", 
                "strArea": "Italian",
                "strInstructions": "Cook pasta with tomatoes and garlic.",
                "strMealThumb": "http://example.com/image.jpg",
                "strTags": "pasta,italian",
                "strIngredient1": "Pasta",
                "strMeasure1": "200g",
                "strIngredient2": "Tomatoes",
                "strMeasure2": "3 pieces"
            }
        ]
        
        # Test upsert
        count = upsert_meals(meals)
        assert count == 1
        
        # Test search
        results = search_meals("pasta")
        assert len(results) >= 1
        assert results[0]["name"] == "Test Pasta"
        
        results = search_meals("tomatoes")
        assert len(results) >= 1
        
        print("✅ Database tests passed")


def run_tests():
    """Run all tests."""
    print("Running MealDB RAG System Tests")
    print("=" * 40)
    
    test_cache()
    test_database()
    
    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_tests()
