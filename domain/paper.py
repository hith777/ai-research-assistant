from tools.pdf_parser import PDFParser
from domain.text_chunk import Chunk
from typing import Optional, List
from tools.text_chunker import TextChunker
from tools.author_cache import AuthorCache
from domain.paper_index import PaperIndex


class Paper:
    def __init__(self, title: str, authors: list[str], source: str, raw_text: str):
        self._title = title
        self._authors = authors
        self._source = source
        self._raw_text = raw_text
        self._chunks: Optional[List[Chunk]] = []
    
    @classmethod
    def from_pdf(cls, pdf_path: str, metadata: dict = None) -> Optional["Paper"]:
        parsed_file = PDFParser.extract_info(pdf_path)
        raw_text = parsed_file["raw_text"]
        with open("cache/raw_extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)


        if metadata:
            title = metadata.get("title", "")
            authors = metadata.get("authors", [])
        else:
            from utils.token_counter import TokenCounter
            from services.metadata_extractor import extract_metadata_with_llm

            metadata_chunk = TokenCounter.get_token_chunk(raw_text, token_limit=800)
            metadata = extract_metadata_with_llm(metadata_chunk)

            title = metadata.get("title", "")
            authors = metadata.get("authors", [])
        
        if title and authors:
            AuthorCache.add_paper(title=title, authors=authors, path=pdf_path)
            PaperIndex.add_paper(title=title, authors=authors, path=pdf_path)

        return cls(title=title, authors=authors, source=pdf_path, raw_text=raw_text)
    
    def chunk_text(self, max_tokens: int = 500, overlap: int = 50) -> Optional[List[Chunk]]:
        """
        Splits the raw text into chunks of a specified maximum token count with overlap.
        :param max_tokens: The maximum number of tokens per chunk.
        :param overlap: The number of overlapping tokens between chunks.
        :return: A list of Chunk objects.
        """
        if self._raw_text:
            self._chunks = TextChunker.chunk_text(self._raw_text, max_tokens, overlap)
            return self._chunks
        return None

    def __str__(self):
        return (
            f"Paper: {self._title}\n"
            f"Authors: {', '.join(self._authors)}\n"
            f"Source: {self._source}\n"
            f"Chunks: {len(self._chunks) if self._chunks else 0}"
        )

    def to_dict(self) -> dict:
        return {
            "title": self._title,
            "authors": self._authors,
            "source": self._source,
            "chunks": [chunk.to_dict() for chunk in self._chunks] if self._chunks else [],
        }

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def authors(self) -> list[str]:
        return self._authors
    
    @property
    def source(self) -> str:
        return self._source
    
    @property
    def raw_text(self) -> str:
        return self._raw_text

    @property
    def chunks(self) -> Optional[List[Chunk]]:
        return self._chunks