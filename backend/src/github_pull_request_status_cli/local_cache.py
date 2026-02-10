from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from platformdirs import user_cache_dir


@dataclass
class CachedValue:
    value: Any
    expires_at_unix_epoch_seconds: float


class LocalTimeToLiveCache:
    def __init__(self, *, application_name: str = "github_pull_request_status_cli", default_time_to_live_seconds: int = 90) -> None:
        self.default_time_to_live_seconds = max(1, int(default_time_to_live_seconds))
        self.cache_directory = Path(user_cache_dir(application_name))
        self.cache_directory.mkdir(parents=True, exist_ok=True)

        self.cache_file_path = self.cache_directory / "cache.json"
        self.in_memory_cache: dict[str, CachedValue] = {}
        self.has_loaded_cache_file = False

    def _current_time_seconds(self) -> float:
        return time.time()

    @staticmethod
    def _hash_cache_key(cache_key: str) -> str:
        return hashlib.sha256(cache_key.encode("utf-8")).hexdigest()

    def _load_cache_file_if_needed(self) -> None:
        if self.has_loaded_cache_file:
            return
        self.has_loaded_cache_file = True

        if not self.cache_file_path.exists():
            return

        try:
            raw_text = self.cache_file_path.read_text(encoding="utf-8")
            parsed_json = json.loads(raw_text)
            if not isinstance(parsed_json, dict):
                return

            for hashed_key, stored_object in parsed_json.items():
                if not isinstance(stored_object, dict):
                    continue
                expires_at = float(stored_object.get("expires_at_unix_epoch_seconds", 0))
                value = stored_object.get("value")
                self.in_memory_cache[str(hashed_key)] = CachedValue(value=value, expires_at_unix_epoch_seconds=expires_at)
        except Exception:
            return

    def _persist_cache_file(self) -> None:
        try:
            serializable_cache: dict[str, Any] = {}
            current_time = self._current_time_seconds()

            for hashed_key, cached_value in self.in_memory_cache.items():
                if cached_value.expires_at_unix_epoch_seconds <= current_time:
                    continue
                serializable_cache[hashed_key] = {
                    "expires_at_unix_epoch_seconds": cached_value.expires_at_unix_epoch_seconds,
                    "value": cached_value.value,
                }

            self.cache_file_path.write_text(json.dumps(serializable_cache, ensure_ascii=False), encoding="utf-8")
        except Exception:
            return

    def get_cached_value(self, cache_key: str) -> Optional[Any]:
        self._load_cache_file_if_needed()
        hashed_key = self._hash_cache_key(cache_key)

        cached_value = self.in_memory_cache.get(hashed_key)
        if cached_value is None:
            return None

        if cached_value.expires_at_unix_epoch_seconds <= self._current_time_seconds():
            self.in_memory_cache.pop(hashed_key, None)
            self._persist_cache_file()
            return None

        return cached_value.value

    def set_cached_value(self, cache_key: str, value: Any, *, time_to_live_seconds: Optional[int] = None) -> None:
        self._load_cache_file_if_needed()
        effective_ttl = self.default_time_to_live_seconds if time_to_live_seconds is None else max(1, int(time_to_live_seconds))
        hashed_key = self._hash_cache_key(cache_key)

        self.in_memory_cache[hashed_key] = CachedValue(
            value=value,
            expires_at_unix_epoch_seconds=self._current_time_seconds() + effective_ttl,
        )
        self._persist_cache_file()

    def clear_all_cached_values(self) -> None:
        self.in_memory_cache.clear()
        try:
            if self.cache_file_path.exists():
                self.cache_file_path.unlink()
        except Exception:
            pass
