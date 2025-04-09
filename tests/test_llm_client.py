import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.llm_client import LLMClient
from dotenv import load_dotenv

load_dotenv()

def test_llm_chat_completion_returns_expected_structure():
    client = LLMClient(provider="openai", model="gpt-3.5-turbo")
    prompt = "Reply with the word 'pong' only."
    
    response = client.chat_completion(prompt)
    
    assert isinstance(response, dict)
    assert "text" in response
    assert "usage" in response
    assert isinstance(response["text"], str)
    assert isinstance(response["usage"], dict)
    assert "total_tokens" in response["usage"]

def test_llm_health_check_ok():
    result = LLMClient.health_check(provider="openai", model="gpt-3.5-turbo")

    assert isinstance(result, dict)
    assert result["status"] == "ok", f"Health check failed: {result['message']}"
    assert "message" in result
