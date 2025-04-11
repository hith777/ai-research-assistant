import os
import json

CACHE_FILE = "cache/author_index.json"

class AuthorCache:
    @staticmethod
    def _load_cache() -> dict:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_cache(cache: dict):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

    @staticmethod
    def add_paper(title: str, authors: list, path: str):
        cache = AuthorCache._load_cache()
        for author in authors:
            key = author.lower()
            entry = {"title": title, "path": path}
            if key not in cache:
                cache[key] = [entry]
            else:
                if not any(p["path"] == path for p in cache[key]):
                    cache[key].append(entry)
        AuthorCache._save_cache(cache)

    @staticmethod
    def get_by_author(name: str) -> list:
        cache = AuthorCache._load_cache()
        return cache.get(name.lower(), [])
