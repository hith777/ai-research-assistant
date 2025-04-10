from typing import Optional
from agents.llm_client import LLMClient

def extract_metadata_with_llm(text: str, llm: Optional[LLMClient] = None) -> dict:
    """
    Uses the LLM to extract metadata like title and authors from the top portion of the paper.

    Args:
        text (str): First 800–1000 tokens of the paper.
        llm (LLMClient, optional): The LLM client to use. Falls back to default.

    Returns:
        dict: {
            "title": str,
            "authors": list[str]
        }
    """
    llm = llm or LLMClient()

    prompt = (
        "You are a research assistant. Your task is to extract metadata from the beginning of a research paper.\n"
        "Please extract the following:\n"
        "- Title of the paper (string)\n"
        "- List of authors (list of strings)\n\n"
        "If you cannot find this information, return empty fields.\n"
        "Respond with a valid JSON object with keys: 'title', 'authors'.\n\n"
        f"Text:\n{text.strip()}"
    )

    try:
        response = llm.chat_completion(prompt)
        import json
        metadata = json.loads(response["text"])

        return {
            "title": metadata.get("title", "").strip(),
            "authors": metadata.get("authors", [])
        }

    except Exception as e:
        print(f"[ERROR] Failed to extract metadata via LLM: {e}")
        return {
            "title": "",
            "authors": []
        }
