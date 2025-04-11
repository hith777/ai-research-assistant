import os
from typing import List
from domain.paper import Paper
from tools.author_cache import AuthorCache

class AuthorSearch:
    @staticmethod
    def search_by_author(name: str, folder_path: str) -> List[dict]:
        """
        Searches a folder for PDF papers written by the given author.

        Args:
            name (str): Author name to search for.
            folder_path (str): Path to folder containing PDFs.

        Returns:
            List of matched papers (dicts with title, authors, path).
        """
        cached = AuthorCache.get_by_author(name)
        if cached:
            return cached

        # Optional fallback: scan folder
        matches = []
        name_lower = name.lower()

        if folder_path:
            for filename in os.listdir(folder_path):
                if not filename.lower().endswith(".pdf"):
                    continue
                full_path = os.path.join(folder_path, filename)
                try:
                    paper = Paper.from_pdf(full_path)
                    if any(name_lower in a.lower() for a in paper.authors):
                        matches.append({
                            "title": paper.title,
                            "authors": paper.authors,
                            "path": full_path
                        })
                except Exception as e:
                    print(f"[WARN] Skipping {filename}: {e}")

        return matches
