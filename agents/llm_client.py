from infra.config import Config
from typing import Optional
from openai import OpenAI

class LLMClient:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self._provider = provider or Config.LLM_PROVIDER
        self._model = model or Config.OPENAI_MODEL
        self._client = self._init_client()
    
    def _init_client(self):
        if self._provider.lower() == "openai":
            return OpenAI(api_key=Config.OPENAI_API_KEY)

        raise NotImplementedError(f"LLM provider '{self._provider}' is not supported yet.")

    def chat_completion(self, prompt: str) -> dict:
        """
        Sends a prompt to the current LLM provider and returns the response text along with token usage.

        Args:
            prompt (str): The prompt to send to the language model.

        Returns:
            dict: {
                "text": str,  # The generated message
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                }
            }
        """
        if self._provider.lower() == "openai":
            try:
                response = self._client.chat.completions.create(
                    model = self._model,
                    messages = [
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                )
                message_text = response.choices[0].message.content.strip()
                usage = response.usage

                return {
                    "text": message_text,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    }
                }
            except Exception as e:
                print(f"[ERROR] OpenAI chat completion failed: {e}")
                return {
                    "text": "",
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
            
        raise NotImplementedError(f"chat_completion is not implemented for provider '{self._provider}'")




