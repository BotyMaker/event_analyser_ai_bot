import asyncio
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..models import SessionLocal, News, Claim, NewsCreate, ClaimCreate
from .schemas import SearchResult, NewsWithClaims
from .claims import ClaimsExtractionService


class NewsStorageService:
    def __init__(self):
        self.claims_service = ClaimsExtractionService()
    
    async def get_or_create_news_with_claims(self, search_results: List[SearchResult]) -> List[NewsWithClaims]:
        """Get or create news entries with claims extracted, returned as NewsWithClaims."""
        tasks = [self._process_single_news(result) for result in search_results]
        return await asyncio.gather(*tasks)
    
    async def _process_single_news(self, search_result: SearchResult) -> NewsWithClaims:
        """Process single news: get from DB or create with claims."""
        with SessionLocal() as db:
            # Check if news exists with eager loading of claims
            stmt = select(News).options(selectinload(News.claims)).where(News.url == search_result.url)
            news = db.scalar(stmt)
            
            if news:
                if news.claims_extracted:
                    # Convert to NewsWithClaims within session context
                    return NewsWithClaims(
                        title=news.title,
                        url=news.url,
                        content=news.content,
                        claims=[claim.text for claim in news.claims],
                        published_date=news.published_date
                    )
                else:
                    # Extract claims for existing news
                    claims_text = await self.claims_service.extract_claims(news.content)
                    await self._add_claims_to_news(news.id, claims_text)
                    news.claims_extracted = True
                    db.commit()
                    
                    # Refresh and return as NewsWithClaims
                    db.refresh(news)
                    return NewsWithClaims(
                        title=news.title,
                        url=news.url,
                        content=news.content,
                        claims=claims_text,
                        published_date=news.published_date
                    )
            else:
                # Create new news with claims
                return await self._create_news_with_claims(search_result)
    
    async def _create_news_with_claims(self, search_result: SearchResult) -> NewsWithClaims:
        """Create new news entry with extracted claims."""
        with SessionLocal() as db:
            # Create news
            news_data = NewsCreate(
                url=search_result.url,
                title=search_result.title,
                content=search_result.text,
                published_date=search_result.published_date
            )
            news = News(**news_data.model_dump())
            db.add(news)
            db.flush()
            
            # Extract and add claims
            claims_text = await self.claims_service.extract_claims(search_result.text)
            for claim_text in claims_text:
                claim = Claim(news_id=news.id, text=claim_text)
                db.add(claim)
            
            news.claims_extracted = True
            db.commit()
            
            # Return as NewsWithClaims (no session dependency)
            return NewsWithClaims(
                title=news.title,
                url=news.url,
                content=news.content,
                claims=claims_text,
                published_date=news.published_date
            )
    
    async def _add_claims_to_news(self, news_id: int, claims_text: List[str]) -> None:
        """Add claims to existing news."""
        with SessionLocal() as db:
            for claim_text in claims_text:
                claim = Claim(news_id=news_id, text=claim_text)
                db.add(claim)
            db.commit() 