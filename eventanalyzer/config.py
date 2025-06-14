import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    exa_api_key: str
    database_url: str

    @classmethod
    def from_env(cls) -> "Config":
        missing = []
        
        telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
            
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            missing.append("OPENAI_API_KEY")
            
        exa_api_key = os.getenv("EXA_API_KEY")
        if not exa_api_key:
            missing.append("EXA_API_KEY")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
        return cls(
            telegram_bot_token=telegram_bot_token,
            openai_api_key=openai_api_key,
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
            openai_model=os.getenv("OPENAI_MODEL", "anthropic/claude-3.5-sonnet"),
            exa_api_key=exa_api_key,
            database_url=os.getenv("DATABASE_URL", "sqlite:///eventanalyzer.db"),
        )


config = Config.from_env() 