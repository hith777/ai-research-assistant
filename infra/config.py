from dotenv import load_dotenv
import os

load_dotenv() # load environment variables from .env file

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOKENS_PER_REQUEST", "3000"))
    MAX_SUMMARY_TOKENS = int(os.getenv("MAX_SUMMARY_TOKENS", "800"))
    MAX_EMBED_TOKENS = int(os.getenv("MAX_EMBED_TOKENS", "8000"))
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"