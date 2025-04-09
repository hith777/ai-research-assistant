import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest
from services.summarizer import SummarizerService
from domain.text_chunk import Chunk

def test_summarize_single_chunk():
    chunk = Chunk(index=0, text="This paper explores reinforcement learning applications in robotics.", token_count=12)
    result = SummarizerService.summarize_chunk(chunk, style="short")
    
    assert isinstance(result, dict)
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0
