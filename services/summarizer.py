from domain.paper import Paper
from domain.chunk import Chunk
from typing import List, Optional
from agents.llm_client import LLMClient


class SummarizerService:
    @staticmethod
    def _build_summary_prompt(chunk: Optional[Chunk], style: str = "default") -> str:
        """
        Builds a prompt to instruct the LLM to summarize a specific text chunk.

        Args:
            chunk (Chunk): The chunk of text to summarize.
            style (str): The style of summarization ('default', 'short', 'layman', 'technical').

        Returns:
            str: A formatted prompt for the LLM.
        """
        if not chunk:
            return ""

        instruction = "Summarize the following part of a research paper clearly and concisely:"

        if style == "short":
            instruction = "Summarize this section briefly in 1-2 sentences:"
        elif style == "layman":
            instruction = "Summarize this section in simple language anyone can understand:"
        elif style == "technical":
            instruction = "Summarize this section with a focus on technical accuracy:"

        return f"{instruction}\n\n{chunk.text.strip()}"

    @staticmethod
    def _build_merge_prompt(chunk_summaries: List[str], style: str = "default") -> str:
        """
        Builds a prompt to instruct the LLM to merge multiple chunk summaries
        into a cohesive overall summary of the paper.

        Args:
            chunk_summaries (List[str]): A list of individual chunk summaries.
            style (str): The desired style of the final paper summary.

        Returns:
            str: A well-structured prompt for the LLM.
        """
        if not chunk_summaries:
            return ""

        # Combine all chunk summaries with section labels
        combined_summaries = "\n\n".join([
            f"Section {i+1} Summary:\n{summary.strip()}"
            for i, summary in enumerate(chunk_summaries)
        ])

        instruction = "Generate a single, clear, and concise overall summary of the entire paper:"

        if style == "short":
            instruction = "Generate a brief, 1-2 sentence summary of the entire paper."
        elif style == "detailed":
            instruction = "Generate a thorough, paragraph-level summary of the entire paper."
        elif style == "layman":
            instruction = "Summarize the entire paper in simple, layman-friendly language."

        return (
            "You are reading a research paper. Below are summaries of its sections.\n"
            f"{instruction}\n\n{combined_summaries}"
        )

    @staticmethod
    def summarize_chunk(chunk: Optional[Chunk], style: str = "default", llm: Optional[LLMClient] = None) -> dict:
        """
        Summarizes a single chunk using the LLM.

        Args:
            chunk (Chunk): The text chunk to summarize.
            style (str): The desired summary style.
            llm (LLMClient, optional): An existing LLMClient instance.

        Returns:
            dict: {
                "summary": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                }
            }
        """
        if not chunk:
            return {"summary": "", "usage": {"total_tokens": 0}}

        llm = llm or LLMClient()
        prompt = SummarizerService._build_summary_prompt(chunk, style)

        try:
            response = llm.chat_completion(prompt)
            return {
                "summary": response["text"],
                "usage": response["usage"]
            }
        except Exception as e:
            print(f"[ERROR] Failed to summarize chunk: {e}")
            return {
                "summary": "",
                "usage": {"total_tokens": 0}
            }

    @staticmethod
    def summarize_paper(chunks: Optional[List[Chunk]], style: str = "default") -> dict:
        """
        Summarizes the entire paper by:
        1. Summarizing each chunk (in default style for consistency),
        2. Merging those summaries into a final summary with the requested style.

        Args:
            chunks (List[Chunk]): List of text chunks to summarize.
            style (str): Final summary style ('default', 'short', 'layman', etc.).

        Returns:
            dict: {
                "final_summary": str,
                "total_usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                }
            }
        """
        if not chunks:
            return {
                "final_summary": "",
                "total_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

        llm = LLMClient()
        chunk_summaries = []
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0

        for chunk in chunks:
            # Always summarize chunks in 'default' style for clarity and accuracy
            response = SummarizerService.summarize_chunk(chunk, "default", llm)
            chunk_summaries.append(response["summary"])

            usage = response["usage"]
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)
            total_tokens += usage.get("total_tokens", 0)

        # Build merge prompt in final desired style
        prompt = SummarizerService._build_merge_prompt(chunk_summaries, style)

        try:
            merge_response = llm.chat_completion(prompt)
            final_summary = merge_response["text"]
            merge_usage = merge_response["usage"]

            # Add merge token usage
            total_prompt_tokens += merge_usage.get("prompt_tokens", 0)
            total_completion_tokens += merge_usage.get("completion_tokens", 0)
            total_tokens += merge_usage.get("total_tokens", 0)

            # Validate final result
            if not final_summary.strip():
                print("[WARNING] Final summary is empty.")
            elif len(final_summary.split()) < 20:
                print(f"[WARNING] Final summary seems very short ({len(final_summary.split())} words):\n{final_summary}")

            return {
                "final_summary": final_summary,
                "total_usage": {
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "total_tokens": total_tokens
                }
            }

        except Exception as e:
            print(f"[ERROR] Failed to summarize the paper: {e}")
            return {
                "final_summary": "",
                "total_usage": {
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "total_tokens": total_tokens
                }
            }
