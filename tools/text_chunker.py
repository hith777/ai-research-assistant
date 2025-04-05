import tiktoken
from typing import List
from domain.chunk import Chunk

class TextChunker:

    @staticmethod
    def chunk_text(text: str, max_tokens: int = 500, overlap: int = 50) -> List[Chunk]:
        """
        Splits the text into chunks of a specified maximum token count with overlap.
        :param text: The text to be chunked.
        :param max_tokens: The maximum number of tokens per chunk.
        :param overlap: The number of overlapping tokens between chunks.
        :return: A list of Chunk objects.
        """
        try:
            max_tokens = max(10, max_tokens - 5)  # Token buffer

            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokens = encoding.encode(text)

            chunks = []
            start = 0
            index = 0

            while start < len(tokens):
                end = min(start + max_tokens, len(tokens))
                chunk_tokens = tokens[start:end]
                chunk_text = encoding.decode(chunk_tokens)
                token_count = len(chunk_tokens)

                chunks.append(Chunk(index=index, text=chunk_text, token_count=token_count))

                index += 1
                start += (max_tokens - overlap)

            return chunks
        except Exception as e:
            print(f"[ERROR] Text chunking failed: {e}")
            return []