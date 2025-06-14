from typing import List
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from ..config import config


class ExtractedClaim(BaseModel):
    text: str = Field(description="A specific factual claim from the news article")


class ClaimsExtraction(BaseModel):
    claims: List[ExtractedClaim] = Field(description="List of factual claims extracted from the article")


class ClaimsExtractionService:
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
    
    async def extract_claims(self, news_text: str) -> List[str]:
        """Extract factual claims from news article."""
        template = self.jinja_env.get_template("claims_extraction.j2")
        prompt = template.render(news_text=news_text)
        
        response = self.client.chat.completions.create(
            model=config.openai_model,
            response_model=ClaimsExtraction,
            messages=[
                {"role": "system", "content": "You are an expert fact-checker. Extract specific, verifiable claims from news articles. Your answer should be not more than 1000 characters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        return [claim.text for claim in response.claims] 