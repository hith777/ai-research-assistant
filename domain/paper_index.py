# domain/paper_index.py

import os
import json
from difflib import SequenceMatcher

PAPER_INDEX_FILE = "cache/paper_index.json"

class PaperIndex:
    @staticmethod
    def _load_index() -> list[dict]:
        if not os.path.exists(PAPER_INDEX_FILE):
            return []
        with open(PAPER_INDEX_FILE, "r") as f:
            return json.load(f)
    
    @staticmethod
    def load_all() -> list:
        if not os.path.exists(PAPER_INDEX_FILE):
            return []

        with open(PAPER_INDEX_FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def fuzzy_match_title(query: str, threshold: float = 0.6) -> list[dict]:
        query = query.lower().strip()
        papers = PaperIndex._load_index()
        matches = []

        for paper in papers:
            score = SequenceMatcher(None, paper["title"].lower(), query).ratio()
            if score >= threshold:
                paper["score"] = round(score, 3)
                matches.append(paper)

        return sorted(matches, key=lambda x: x["score"], reverse=True)

    @staticmethod
    def add_paper(title: str, authors: list[str], path: str):
        paper = {
            "title": title.strip(),
            "authors": [a.strip() for a in authors],
            "path": path
        }

        index = PaperIndex._load_index()

        # Avoid duplicates
        for entry in index:
            if entry["title"].lower() == paper["title"].lower() and entry["path"] == path:
                return  # already added

        index.append(paper)
        with open(PAPER_INDEX_FILE, "w") as f:
            json.dump(index, f, indent=2)

