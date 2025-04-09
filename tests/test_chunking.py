import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.text_chunker import TextChunker
from domain.text_chunk import Chunk

def test_chunk_text_splits_long_input():
    long_text = "This is a sentence. " * 200 

    chunks = TextChunker.chunk_text(long_text, max_tokens=100, overlap=20)

    assert isinstance(chunks, list)
    assert all(isinstance(c, Chunk) for c in chunks)
    assert len(chunks) > 1 

def test_chunk_overlap():
    text = "This is sentence one. This is sentence two. This is sentence three." * 50
    chunks = TextChunker.chunk_text(text, max_tokens=80, overlap=40)

    for i in range(1, len(chunks)):
        prev = chunks[i - 1].text
        curr = chunks[i].text
        overlap_found = any(sentence.strip() in prev for sentence in curr.split("."))
        assert overlap_found, f"Chunk {i} does not overlap with previous chunk."
