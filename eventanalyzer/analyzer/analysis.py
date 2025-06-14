from typing import List
import instructor
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from ..config import config
from .schemas import NewsAnalysis, NewsWithClaims, InitialNewsWithClaims


class AnalysisService:
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
    
    async def analyze_news(self, initial_news: InitialNewsWithClaims, sources: List[NewsWithClaims]) -> NewsAnalysis:
        """Analyze news for inaccuracies using a simplified claim comparison."""
        template = self.jinja_env.get_template("analysis_with_claims.j2")
        prompt = template.render(
            initial_news=initial_news,
            sources=sources
        )
        
        response = self.client.chat.completions.create(
            model=config.openai_model,
            response_model=NewsAnalysis,
            messages=[
                {"role": "system", "content": "You are a professional fact-checker. Your goal is to provide a clear, concise analysis of news claims based on provided sources. Your answer should be not more than 10000 characters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        return response 