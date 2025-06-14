from typing import List
from exa_py import Exa

from ..config import config
from .schemas import SearchResult


class NewsSearchService:
    def __init__(self):
        self.exa = Exa(config.exa_api_key)
    
    async def search_related_news(self, news_text: str, num_results: int = 10) -> List[SearchResult]:
        """Search for related news articles using Exa."""
        try:
            results = self.exa.search_and_contents(
                query=news_text,
                type="neural",
                use_autoprompt=True,
                num_results=num_results,
                text=True,
            )
            
            return [
                SearchResult(
                    title=result.title,
                    url=result.url,
                    text=result.text[:2000],
                    published_date=getattr(result, 'published_date', None)
                )
                for result in results.results
            ]
        except Exception as e:
            # Fallback to keyword search if neural search fails
            return await self._fallback_search(news_text, num_results)
    
    async def _fallback_search(self, news_text: str, num_results: int) -> List[SearchResult]:
        """Fallback keyword-based search."""
        try:
            results = self.exa.search_and_contents(
                query=news_text[:100],  # Use first 100 chars as keywords
                type="keyword",
                num_results=num_results,
                text=True
            )
            
            return [
                SearchResult(
                    title=result.title,
                    url=result.url,
                    text=result.text[:2000],
                    published_date=getattr(result, 'published_date', None)
                )
                for result in results.results
            ]
        except Exception:
            return [] 