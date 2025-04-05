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

        Returns:
            str: A well-structured prompt for the LLM.
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
    def _build_merge_prompt(chunk_summaries: Optional[List[Chunk]], style: str = "default") -> str:
        """
        Builds a prompt to instruct the LLM to merge multiple summaries into a single summary.

        Args:
            chunk_summaries (List[Chunk]): The list of chunk summaries to merge.

        Returns:
            str: A well-structured prompt for the LLM.
        """
        if not chunk_summaries:
            return ""
        
        combined_summaries = "\n\n".join([f"Section {i+1} Summary:\n{chunk.text.strip()}" for i, chunk in enumerate(chunk_summaries)])

        instruction = "Generate a single, clear, and concise overall summary of the entire paper:"

        if style == "short":
            instruction = "Generate a brief, 1-2 sentence summary of the entire paper."
        elif style == "detailed":
            instruction = "Generate a thorough, paragraph-level summary of the entire paper."
        elif style == "layman":
            instruction = "Summarize the entire paper in simple, layman-friendly language."


        return f"You are reading a research paper. Below are summaries of its sections.\n{instruction}\n\n{combined_summaries}"

    @staticmethod
    def summarize_chunk(chunk: Optional[Chunk], style: str = "default", llm: Optional[LLMClient] = None) -> str:
        """
        Summarizes a given chunk of text using the LLM client. Map step in the pipeline.
        
        Args:
            chunk (Chunk): The chunk to summarize.
        
        Returns:
            str: The summarized text.
        """
        if not chunk:
            return ""

        llm = llm or LLMClient()
        prompt = SummarizerService._build_summary_prompt(chunk, style)
        
        try:
            return llm.chat_completion(prompt)
        except Exception as e:
            print(f"[ERROR] failed to summarize the chunk: {e}")
            return ""

    @staticmethod
    def summarize_paper(chunks: Optional[List[Chunk]], style: str = "default") -> str:
        """
        Generates a final, merged summary for a paper by summarizing all chunks
        and combining them into a single cohesive summary.

        Args:
            chunks (List[Chunk]): List of text chunks to summarize.
            style (str): The style of summarization ('default', 'short', 'layman', etc.).

        Returns:
            str: A complete summary of the paper.
        """
        if not chunks:
            return ""

        llm = LLMClient()
        chunk_summaries = [SummarizerService.summarize_chunk(chunk, style, llm) for chunk in chunks]

        prompt = SummarizerService._build_merge_prompt(chunk_summaries, style)

        try:
            return llm.chat_completion(prompt)
        except Exception as e:
            print(f"[ERROR] failed to summarize the paper: {e}")
            return ""
        

        


        
        