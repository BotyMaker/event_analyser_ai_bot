import logging
from .search import NewsSearchService
from .analysis import AnalysisService
from .storage import NewsStorageService
from .claims import ClaimsExtractionService
from .message import MessageGenerationService
from .schemas import NewsAnalysis, InitialNewsWithClaims, InitialNews

logger = logging.getLogger(__name__)


class NewsAnalysisPipeline:
    def __init__(self):
        self.search_service = NewsSearchService()
        self.analysis_service = AnalysisService()
        self.storage_service = NewsStorageService()
        self.claims_service = ClaimsExtractionService()
        self.message_service = MessageGenerationService()
    
    async def analyze(self, news_text: str, custom_instruction: str = None) -> str:
        """Complete news analysis pipeline, returning a user-ready message."""
        logger.info("Starting simplified news analysis pipeline")
        try:
            analysis = await self.analyze_detailed(news_text)
            initial_news = InitialNews(text=news_text)
            logger.info("Generating final user message")
            final_message = await self.message_service.generate_telegram_message(analysis, initial_news, custom_instruction)
            logger.info("Pipeline completed successfully")
            return final_message
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
    
    async def analyze_detailed(self, news_text: str) -> NewsAnalysis:
        """Run the analysis and return the detailed NewsAnalysis object."""
        logger.info("Extracting claims from initial news")
        initial_claims = await self.claims_service.extract_claims(news_text)
        initial_news = InitialNewsWithClaims(
            content=news_text,
            claims=initial_claims
        )
        logger.info(f"Extracted {len(initial_claims)} initial claims")
        
        logger.info("Searching for related sources")
        search_results = await self.search_service.search_related_news(news_text)
        logger.info(f"Found {len(search_results)} related sources")
        
        logger.info("Processing sources to extract their claims")
        sources = await self.storage_service.get_or_create_news_with_claims(search_results)
        logger.info(f"Processed {len(sources)} sources with claims")
        
        logger.info("Performing simplified claim analysis")
        analysis = await self.analysis_service.analyze_news(initial_news, sources)
        logger.info(f"Analysis complete. Score: {analysis.credibility_score}/10. "
                    f"Supported: {len(analysis.supported_claims)}. "
                    f"Contradicted: {len(analysis.contradictory_claims)}.")
        return analysis 