import instructor
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime

from ..config import config
from .schemas import NewsAnalysis, InitialNews


class TelegramMessage(BaseModel):
    text: str = Field(description="Ready-to-send Telegram message text")


class MessageGenerationService:
    def __init__(self):
        self.client = instructor.from_openai(
            OpenAI(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url
            ),
            mode=instructor.Mode.JSON
        )
        
        template_dir = Path(__file__).parent / "prompts"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def generate_telegram_message(self, analysis: NewsAnalysis, initial_news: InitialNews, custom_instruction: str = None) -> str:
        """Generate user-friendly Telegram message from analysis results."""
        template = self.jinja_env.get_template("telegram_message.j2")
        prompt = template.render(
            analysis=analysis,
            initial_news=initial_news,
            custom_instruction=custom_instruction or "Please provide a neutral and objective analysis."
        )
        
        response = self.client.chat.completions.create(
            model=config.openai_model,
            response_model=TelegramMessage,
            messages=[
                {"role": "system", "content": f"You are a professional news analyst creating clear, engaging messages for Telegram users. Today is {datetime.now().strftime('%Y-%m-%d')}. Your answer should be not more than 2500 characters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        return response.text 