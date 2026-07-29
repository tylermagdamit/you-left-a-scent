"""HTTP request models for the scent API."""

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    vibe: str = Field(min_length=1, max_length=280)
    count: int = Field(default=5, ge=3, le=5)
