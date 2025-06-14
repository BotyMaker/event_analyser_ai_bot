from typing import List, Optional
from pydantic import BaseModel, Field


class VerifiedClaim(BaseModel):
    """A claim from the initial news verified against a source."""
    initial_claim: str = Field(description="The claim from the original news article.")
    source_claim: str = Field(description="The specific claim from the source that supports or contradicts the original claim.")
    source_url: str = Field(description="The URL of the source article.")
    source_title: str = Field(description="The title of the source article.")
    explanation: str = Field(description="A brief explanation of how the source claim supports or contradicts the original claim.")


class SearchResult(BaseModel):
    title: str = Field(description="The title of the news article")
    url: str = Field(description="The URL of the news article")
    text: str = Field(description="The content of the news article")
    published_date: str = Field(None, description="The publication date of the article")


class InitialNews(BaseModel):
    text: str = Field(description="The text of the initial news article")


class NewsAnalysis(BaseModel):
    """A simplified fact-checking analysis of a news article."""
    summary: str = Field(description="A brief summary of the overall findings of the fact-check analysis.")
    credibility_score: int = Field(description="A credibility score from 1-10 for the original news article.", ge=1, le=10)
    supported_claims: List[VerifiedClaim] = Field(description="A list of claims from the original article that were supported by the sources.")
    contradictory_claims: List[VerifiedClaim] = Field(description="A list of claims from the original article that were contradicted by the sources.")
    unverified_claims: List[str] = Field(description="A list of claims from the original article that could not be verified from the sources.")


class NewsWithClaims(BaseModel):
    """News article with extracted claims for analysis."""
    title: str
    url: str
    content: str
    claims: List[str]
    published_date: Optional[str] = None


class InitialNewsWithClaims(BaseModel):
    """Initial news with extracted claims for comparison."""
    content: str
    claims: List[str] 