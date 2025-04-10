from domain.paper import Paper
from domain.text_chunk import Chunk
from typing import List, Optional
from infra.config import Config
from tools.cost_tracker import CostTracker
from agents.llm_client import LLMClient
from utils.message_utils import (build_compression_prompt, build_compressed_summary_prompt, build_summary_prompt)
from utils.token_counter import TokenCounter


class SummarizerService:
    
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
                },
                used_compression: bool
            }
        """
        if not chunk:
            return {"summary": "", "usage": {"total_tokens": 0}}

        llm = llm or LLMClient()
        prompt = build_summary_prompt(chunk, style)

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
    def summarize_paper(path: str, style: str = "default", llm: Optional[LLMClient] = None, provider: Optional[str] = None, model: Optional[str] = None) -> dict:
        """
        Summarizes the entire paper by:
        1. Compressing all chunks (preserving technical accuracy),
        2. Generating a styled summary from the full compressed content.

        Args:
            path (str): file path to the paper.
            style (str): Final summary style ('default', 'short', 'layman', etc.).
            llm (LLMClient, optional): Optional shared LLMClient instance.

        Returns:
            dict: {
                "final_summary": str,
                "title": str,
                "authors": List[str],
                "style": str,
                "source": str,
                "total_usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "cost": float
            }
        """
        if not path:
            return {
                "final_summary": "",
                "title": "",
                "authors": [],
                "style": "",
                "source": "full_text",
                "chunks": 0,
                "total_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "cost": 0.0

            }

        llm = llm or LLMClient(provider, model)

        #Step 1: Compress the full paper
        paper = Paper.from_pdf(path)
        paper.chunk_text()
        compression = SummarizerService.compress_paper(paper.chunks, llm)
        compressed_text = compression["compressed_text"]
        compression_usage = compression["usage"]


        #Step 2: Build final prompt from the compressed version
        final_prompt = build_compressed_summary_prompt(compressed_text, style)

        try:
            summary_response = llm.chat_completion(final_prompt)
            summary_usage = summary_response["usage"]

            total_prompt = compression_usage.get("prompt_tokens", 0) + summary_usage.get("prompt_tokens", 0)
            total_completion = compression_usage.get("completion_tokens", 0) + summary_usage.get("completion_tokens", 0)
            total_tokens = compression_usage.get("total_tokens", 0) + summary_usage.get("total_tokens", 0)

            return {
                "final_summary": summary_response["text"],
                "title": paper.title,
                "authors": paper.authors,
                "style": style,
                "source": "compressed" if compression.get("used_compression") else "full_text",
                "chunks": len(paper.chunks),
                "total_usage": {
                    "prompt_tokens": total_prompt,
                    "completion_tokens": total_completion,
                    "total_tokens": total_tokens,
                },
                "cost": CostTracker.estimate_cost(
                    prompt_tokens=total_prompt,
                    completion_tokens=total_completion,
                    cost_per_1k_tokens=llm.costs
                )
            }

        except Exception as e:
            print(f"[ERROR] Failed to summarize compressed paper: {e}")
            return {
                "final_summary": "",
                "title": "",
                "authors": [],
                "style": "",
                "source": "full_text",
                "chunks": 0,
                "total_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }

            }

    @staticmethod
    def compress_paper(chunks: List[Chunk], llm: Optional[LLMClient] = None) -> dict:
        """
        Compresses all chunks of a paper into a single technical representation.

        Args:
            chunks (List[Chunk]): The full set of paper chunks.
            llm (LLMClient, optional): Reusable LLM client instance.

        Returns:
            dict: {
                "compressed_text": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                }
            }
        """
        if not chunks:
            return {"compressed_text": "", "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "used_compression": False}

        llm = llm or LLMClient()

        full_text = "\n\n".join(chunk.text for chunk in chunks)
        total_tokens = TokenCounter.count_tokens(full_text)

        if total_tokens < TokenCounter.get_max_tokens():
            # Summarize the entire raw paper in one go (no compression)
            prompt = "Summarize the following research paper text concisely, preserving all technical detail:\n\n" + full_text
            response = llm.chat_completion(prompt)
            return {
                "compressed_text": response["text"],
                "usage": response["usage"],
                "used_compression": False
            }

        compressed_sections = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for chunk in chunks:
            prompt = build_compression_prompt(chunk.text)
            try:
                response = llm.chat_completion(prompt)
                compressed_sections.append(response["text"])

                usage = response["usage"]
                total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
                total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                total_usage["total_tokens"] += usage.get("total_tokens", 0)

            except Exception as e:
                print(f"[ERROR] Failed to compress chunk: {e}")

        return {
            "compressed_text": "\n\n".join(compressed_sections),
            "usage": total_usage,
            "used_compression": True
        }


    
    @staticmethod
    def compare_papers(path1: str, path2: str, style: str = "default", llm: Optional[LLMClient] = None, provider: Optional[str] = None, model: Optional[str] = None) -> dict:
        """
        Compares two research papers by compressing their full content
        and generating a comparison based on goals, methods, and conclusions.

        Args:
            path1 (str): Path to the first PDF.
            path2 (str): Path to the second PDF.
            style (str): Tone of the final comparison (default, layman, etc.)
            llm (LLMClient, optional): Reusable LLM client.

        Returns:
            dict: {
                "comparison": str,
                "style": str,
                "source": str,
                "total_usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "cost": float,
                "paper_1": {
                    "title": str,
                    "authors": List[str]
                },
                "paper_2": {
                    "title": str,
                    "authors": List[str]
                }
            }
        """
        try:
            llm = llm or LLMClient(provider, model)
            paper1 = Paper.from_pdf(path1)
            paper2 = Paper.from_pdf(path2)

            paper1.chunk_text()
            paper2.chunk_text()

            #Compress both papers
            compressed1 = SummarizerService.compress_paper(paper1.chunks, llm)
            compressed2 = SummarizerService.compress_paper(paper2.chunks, llm)

            total_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

            total_usage["prompt_tokens"] += compressed1["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += compressed1["usage"]["completion_tokens"]
            total_usage["total_tokens"] += compressed1["usage"]["total_tokens"]

            total_usage["prompt_tokens"] += compressed2["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += compressed2["usage"]["completion_tokens"]
            total_usage["total_tokens"] += compressed2["usage"]["total_tokens"]

            comparison_prompt = (
                f"You are comparing two full research papers based on their content below.\n\n"
                f"Paper 1:\n{compressed1['compressed_text']}\n\n"
                f"Paper 2:\n{compressed2['compressed_text']}\n\n"
                f"Write a clear comparison covering research focus, methods, technical approach, and conclusions. "
                f"Point out both similarities and differences. Use a {style} tone."
            )

            response = llm.chat_completion(comparison_prompt)
            total_usage["prompt_tokens"] += response["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += response["usage"]["completion_tokens"]
            total_usage["total_tokens"] += response["usage"]["total_tokens"]

            return {
                "comparison": response["text"],
                "style": style,
                "source": "compressed",
                "total_usage": total_usage,
                "cost": CostTracker.estimate_cost(
                    prompt_tokens=total_usage["prompt_tokens"],
                    completion_tokens=total_usage["completion_tokens"],
                    cost_per_1k_tokens=llm._costs
                ),
                "paper_1": {
                    "title": paper1.title,
                    "authors": paper1.authors
                },
                "paper_2": {
                    "title": paper2.title,
                    "authors": paper2.authors
                }
            }

        except Exception as e:
            print(f"[ERROR] Failed to compare papers: {e}")
            return {
                "comparison": "Comparison failed due to an internal error.",
                "style": "",
                "source": "full_text",
                "total_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "cost": 0.0,
                "paper_1": {
                    "title": "",
                    "authors": []
                },
                "paper_2": {
                    "title": "",
                    "authors": []
                }
            }

