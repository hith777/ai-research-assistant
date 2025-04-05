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

    def chat_completion(self, prompt: str):
        """
        Sends a prompt to the current LLM provider and returns the response.

        Args:
            prompt (str): The prompt to send to the language model.

        Returns:
            str: The generated response text.
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
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[ERROR] OpenAI chat completion failed: {e}")
                return ""
            
        raise NotImplementedError(f"chat_completion is not implemented for provider '{self._provider}'")




