import re
import openai
from typing import Optional
from domain.chunk import Chunk

def extract_style_from_messages(thread_id: str, default: str = "default") -> str:
    """
    Attempts to extract a 'style' value from the user's messages in a thread.
    Supports patterns like [style=layman] or inline mentions.

    Args:
        thread_id (str): The OpenAI thread ID.
        default (str): Fallback style if none found.

    Returns:
        str: The extracted or default style in lowercase.
    """
    try:
        messages = openai.beta.threads.messages.list(thread_id=thread_id).data
        for msg in messages:
            if msg.role == "user" and "style=" in msg.content[0].text.value:
                match = re.search(r"style=(\w+)", msg.content[0].text.value)
                if match:
                    return match.group(1).strip().lower()
    except Exception as e:
        print(f"[WARN] Failed to extract style from thread messages: {e}")

    return default


def build_summary_prompt(chunk: Optional[Chunk], style: str = "default") -> str:
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
    

def build_compression_prompt(text: str) -> str:
    """
    Builds a prompt to compress a section of a research paper without losing technical details.

    Args:
        text (str): The raw text from a chunk.

    Returns:
        str: A compression prompt for the LLM.
    """
    return (
        "You are compressing a section of a research paper. "
        "Rewrite the section more concisely, but preserve all technical detail, key terminology, and context.\n\n"
        f"{text.strip()}"
    )


def build_compressed_summary_prompt(compressed_text: str, style: str = "default") -> str:
    """
    Builds a prompt to summarize the full compressed version of a research paper.

    Args:
        compressed_text (str): The full compressed representation of the paper.
        style (str): The style of summarization ('default', 'short', 'layman', 'detailed').

    Returns:
        str: A prompt to instruct the LLM to generate the final summary.
    """
    if style == "short":
        instruction = (
            "You are given a compressed version of a research paper. "
            "Summarize it briefly in 2-3 sentences."
        )
    elif style == "layman":
        instruction = (
            "You are given a compressed version of a research paper. "
            "Explain it in simple, layman-friendly language so anyone can understand it."
        )
    elif style == "detailed":
        instruction = (
            "You are given a compressed version of a research paper. "
            "Provide a thorough, paragraph-level summary that captures the structure and technical depth."
        )
    else:
        instruction = (
            "You are given a compressed version of a research paper. "
            "Summarize it clearly and concisely while preserving its key ideas and structure."
        )

    return f"{instruction}\n\n{compressed_text.strip()}"