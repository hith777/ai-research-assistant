import os
import hashlib
import json

CACHE_DIR = "cache"

class CacheManager:
    @staticmethod
    def _ensure_cache_dir():
        """
        Ensures the cache directory exists.
        """
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """
        Generates a SHA-256 hash of the file contents.
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _get_cache_path(file_hash: str, style: str) -> str:
        """
        Builds the full cache file path for a given file hash and style.
        """
        return os.path.join(CACHE_DIR, f"{file_hash}__{style}.json")

    @staticmethod
    def is_cached(file_hash: str, style: str) -> bool:
        """
        Checks if a cached summary exists for the given hash and style.
        """
        CacheManager._ensure_cache_dir()
        return os.path.exists(CacheManager._get_cache_path(file_hash, style))

    @staticmethod
    def load_cached_summary(file_hash: str, style: str) -> dict:
        """
        Loads the cached summary JSON for a given file hash and style.
        """
        with open(CacheManager._get_cache_path(file_hash, style), "r") as f:
            return json.load(f)

    @staticmethod
    def save_summary(file_hash: str, style: str, summary_data: dict):
        """
        Saves the summary data (final_summary + usage) as a JSON using the given file hash and style.
        """
        CacheManager._ensure_cache_dir()
        with open(CacheManager._get_cache_path(file_hash, style), "w") as f:
            json.dump(summary_data, f, indent=2)