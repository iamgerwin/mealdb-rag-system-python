from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    # API
    themealdb_api_key: str = os.getenv("THEMEALDB_API_KEY", "1")
    themealdb_base_url: str = os.getenv("THEMEALDB_BASE_URL", "https://www.themealdb.com/api/json/v1/1")

    # LLM model via ToolFront
    default_model: str = os.getenv("DEFAULT_MODEL", "openai:gpt-4o")

    # Paths
    root_dir: Path = Path(os.getenv("PROJECT_ROOT", ".")).resolve()
    cache_dir: Path = Path(os.getenv("CACHE_DIR", "./cache")).resolve()
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data")).resolve()
    logs_dir: Path = Path(os.getenv("LOGS_DIR", "./logs")).resolve()

    # Cache
    cache_expiry_hours: int = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Path = Path(os.getenv("LOG_FILE", "./logs/mealdb-rag.log")).resolve()


settings = Settings()
settings.cache_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)
