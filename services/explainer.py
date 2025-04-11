from typing import Optional, List
from domain.paper import Paper
from infra.config import Config
from agents.llm_client import LLMClient
import tiktoken

class TermExplainer:
    @staticmethod
    def explain_term(term: str, paper: Paper, style: str = "default", llm: Optional[LLMClient] = None) -> dict:
        """
        Explains a technical term in the context of the paper.
        - Uses full text if under token limit
        - Falls back to relevant chunks if necessary
        - If not found in paper, uses general knowledge

        Returns:
            dict {
                "term": str,
                "source": "contextual" | "chunked" | "fallback" | "error",
                "summary": str
            }
        """
        llm = llm or LLMClient()
        model = Config.OPENAI_MODEL
        tokenizer = tiktoken.encoding_for_model(model)
        term_lower = term.lower()

        # Estimate token count
        estimated_tokens = len(tokenizer.encode(paper.raw_text))
        source = "contextual"

        # ✅ Case 1: Paper is small enough → use full text
        if estimated_tokens < 10000:
            prompt = (
                f"You are a research assistant. Explain the term '{term}' "
                f"based on the following academic paper content:\n\n"
                f"{paper.raw_text[:12000]}\n\n"
                f"Make it {style.lower() if style != 'default' else 'clear and informative'}."
            )

        else:
            source = "chunked"
            # Lazy chunk only when needed
            if not paper.chunks:
                paper.chunk_text()

            matching_chunks = [c for c in paper.chunks if term_lower in c.text.lower()]

            if matching_chunks:
                context = "\n\n".join([c.text for c in matching_chunks[:3]])
                prompt = (
                    f"You are a research assistant. Based on the following excerpts, explain the term '{term}':\n\n"
                    f"{context}\n\n"
                    f"Make the explanation {style} and grounded in the paper."
                )
            else:
                source = "fallback"
                prompt = (
                    f"The term '{term}' does not appear in the paper. "
                    f"Explain its meaning in general machine learning or AI context."
                )

        try:
            response = llm.chat_completion(prompt)
            return {
                "term": term,
                "source": source,
                "summary": response["text"].strip()
            }

        except Exception as e:
            return {
                "term": term,
                "source": "error",
                "summary": f"[ERROR] {e}"
            }
    
    @staticmethod
    def extract_terms(paper: Paper, llm: Optional[LLMClient] = None, top_n: int = 10) -> List[str]:
        """
        Uses LLM to extract top N key terms or concepts from the paper.
        """
        llm = llm or LLMClient()

        prompt = (
            "Extract the top 10 key technical terms or concepts from this research paper.\n"
            "Only return a list of words or phrases, no extra explanation.\n\n"
            f"{paper.raw_text[:8000]}"
        )

        try:
            response = llm.chat_completion(prompt)
            raw = response["text"].strip()

            # Parse into clean list
            lines = [line.strip("-• ").strip() for line in raw.splitlines() if line.strip()]
            terms = [line for line in lines if len(line.split()) <= 5]
            return terms[:top_n]
        except Exception as e:
            print(f"[ERROR] Failed to extract terms: {e}")
            return []

