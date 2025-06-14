import pytest
from unittest.mock import AsyncMock, patch, ANY

from eventanalyzer.analyzer.pipeline import NewsAnalysisPipeline
from eventanalyzer.analyzer.schemas import NewsAnalysis, VerifiedClaim, SearchResult, InitialNews


@pytest.fixture
def mock_simplified_analysis():
    """Fixture for a simplified NewsAnalysis object."""
    return NewsAnalysis(
        summary="The analysis found mixed results, with some claims supported and others contradicted by sources.",
        credibility_score=6,
        supported_claims=[
            VerifiedClaim(
                initial_claim="Claim A is true.",
                source_claim="Source confirms Claim A.",
                source_url="https://example.com/source1",
                source_title="Source One",
                explanation="The source directly supports the initial claim."
            )
        ],
        contradictory_claims=[
            VerifiedClaim(
                initial_claim="Claim B is false.",
                source_claim="Source states Claim B is actually true.",
                source_url="https://example.com/source2",
                source_title="Source Two",
                explanation="The source directly contradicts the initial claim."
            )
        ],
        unverified_claims=["Claim C could not be verified."]
    )


@pytest.mark.asyncio
async def test_pipeline_analyze_detailed(mock_simplified_analysis):
    """Test that analyze_detailed returns a simplified NewsAnalysis object."""
    pipeline = NewsAnalysisPipeline()

    with patch.object(pipeline.claims_service, 'extract_claims', new_callable=AsyncMock) as mock_claims, \
         patch.object(pipeline.search_service, 'search_related_news', new_callable=AsyncMock) as mock_search, \
         patch.object(pipeline.storage_service, 'get_or_create_news_with_claims', new_callable=AsyncMock) as mock_storage, \
         patch.object(pipeline.analysis_service, 'analyze_news', new_callable=AsyncMock) as mock_analysis:

        mock_claims.return_value = ["Claim A is true.", "Claim B is false.", "Claim C could not be verified."]
        mock_search.return_value = [SearchResult(title="Test", url="https://test.com", text="Test")]
        mock_storage.return_value = []
        mock_analysis.return_value = mock_simplified_analysis

        result = await pipeline.analyze_detailed("Some news text")

        assert result == mock_simplified_analysis
        assert isinstance(result, NewsAnalysis)
        assert len(result.supported_claims) == 1
        assert len(result.contradictory_claims) == 1
        mock_analysis.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_analyze_returns_message(mock_simplified_analysis):
    """Test that analyze returns a final string message."""
    pipeline = NewsAnalysisPipeline()
    final_message = "This is the final formatted message for Telegram."
    news_text = "Some news text"

    with patch.object(pipeline, 'analyze_detailed', new_callable=AsyncMock) as mock_analyze_detailed, \
         patch.object(pipeline.message_service, 'generate_telegram_message', new_callable=AsyncMock) as mock_generate_message:

        mock_analyze_detailed.return_value = mock_simplified_analysis
        mock_generate_message.return_value = final_message

        result = await pipeline.analyze(news_text)

        assert result == final_message
        assert isinstance(result, str)
        mock_analyze_detailed.assert_called_once_with(news_text)
        mock_generate_message.assert_called_once_with(mock_simplified_analysis, ANY, None)
        
        # Verify that the second argument is an InitialNews object with the correct text
        call_args = mock_generate_message.call_args[0]
        assert isinstance(call_args[1], InitialNews)
        assert call_args[1].text == news_text


def test_search_result_schema():
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        text="Test content",
        published_date="2024-01-01"
    )
    
    assert result.title == "Test Title"
    assert result.url == "https://example.com"
    assert result.text == "Test content"
    assert result.published_date == "2024-01-01"


def test_news_analysis_schema():
    analysis = NewsAnalysis(
        summary="Summary of the fact-check analysis",
        credibility_score=5,
        supported_claims=[
            VerifiedClaim(
                initial_claim="Test initial claim",
                source_claim="Source supports this claim",
                source_url="https://example.com",
                source_title="Example Source",
                explanation="The source confirms the claim"
            )
        ],
        contradictory_claims=[],
        unverified_claims=["Unverified claim"]
    )
    
    assert analysis.summary == "Summary of the fact-check analysis"
    assert analysis.credibility_score == 5
    assert len(analysis.supported_claims) == 1
    assert len(analysis.contradictory_claims) == 0
    assert len(analysis.unverified_claims) == 1 