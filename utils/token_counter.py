from infra.config import Config

class TokenCounter:
    @staticmethod
    def count_tokens(text: str, model: str = None) -> int:
        provider = Config.LLM_PROVIDER.lower()
        model = model or Config.OPENAI_MODEL

        if provider == "openai":
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))

        elif provider == "gemini":
            # Gemini uses sentencepiece-like tokenizer
            # from some_gemini_tokenizer import tokenize  # placeholder
            # return len(tokenize(text))
            return

        elif provider == "claude":
            # # Claude uses Claude tokenizer (from Anthropic or transformers)
            # return len(text.split())  # TEMP fallback
            return

        # fallback (not recommended)
        return len(text.split())

    @staticmethod
    def get_max_tokens(model: str = None) -> int:
        provider = Config.LLM_PROVIDER.lower()
        model = model or Config.OPENAI_MODEL

        if provider == "openai":
            return {
                "gpt-3.5-turbo": 4096,
                "gpt-4": 8192,
                "gpt-4-1106-preview": 128000,
            }.get(model, 4096)

        elif provider == "gemini":
            return 30720  # Or 32k based on Gemini Pro

        elif provider == "claude":
            return 100000  # Claude 2/3 supports up to 100K

        return 4096  # default
    
    @staticmethod
    def get_token_chunk(text: str, token_limit: int = 2500, model: str = None) -> str:
        """
        Returns a decoded string from the first N tokens of the text,
        using the appropriate tokenizer if available.

        Args:
            text (str): Full input text.
            token_limit (int): Max number of tokens to extract.
            model (str, optional): LLM model name. Defaults to config.
        """
        provider = Config.LLM_PROVIDER.lower()
        model = model or Config.OPENAI_MODEL

        if provider == "openai":
            try:
                import tiktoken
                encoding = tiktoken.encoding_for_model(model)
                tokens = encoding.encode(text)
                return encoding.decode(tokens[:token_limit])
            except Exception as e:
                print(f"[WARN] OpenAI token chunk fallback: {e}")
                return " ".join(text.split()[:token_limit])

        # Fallback for Claude, Gemini, etc. — rough estimate
        return " ".join(text.split()[:token_limit])

