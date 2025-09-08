from __future__ import annotations
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional

from .config import settings
from .logger import logger


class FileCache:
    def __init__(self, ttl_hours: int | None = None, base_dir: Path | None = None):
        self.ttl_seconds = (ttl_hours or settings.cache_expiry_hours) * 3600
        self.base_dir = (base_dir or settings.cache_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.base_dir / f"{digest}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            ts = payload.get("_ts", 0)
            if self.ttl_seconds > 0 and (time.time() - ts) > self.ttl_seconds:
                logger.debug(f"Cache expired for {key}")
                return None
            return payload.get("data")
        except Exception as e:
            logger.warning(f"Failed reading cache for {key}: {e}")
            return None

    def set(self, key: str, data: Any) -> None:
        path = self._key_to_path(key)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump({"_ts": time.time(), "data": data}, f)
        except Exception as e:
            logger.error(f"Failed writing cache for {key}: {e}")


cache = FileCache()
