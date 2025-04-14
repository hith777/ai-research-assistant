from difflib import SequenceMatcher
from domain.paper_index import PaperIndex

class SearchService:
    @staticmethod
    def search_by_title(query: str, threshold: float = 0.4) -> list:
        query_lower = query.lower()
        matches = []

        for paper in PaperIndex.load_all():
            title = paper.get("title", "")
            similarity = SequenceMatcher(None, query_lower, title.lower()).ratio()

            if similarity >= threshold:
                paper["score"] = round(similarity, 3)
                matches.append(paper)

        # Sort by best match
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches

    @staticmethod
    def similarity_score(q1: str, q2: str) -> float:
        """Simple token overlap score (or replace with fuzzy ratio later)"""
        q1_words = set(q1.split())
        q2_words = set(q2.split())
        overlap = q1_words & q2_words

        return len(overlap) / max(len(q1_words), 1)

