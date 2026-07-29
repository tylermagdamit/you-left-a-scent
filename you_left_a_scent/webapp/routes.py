"""API routes for the scent web application."""

from fastapi import APIRouter, HTTPException

from .schemas import RecommendationRequest
from .service import recommend_for_web


router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/recommend")
def create_recommendation(request: RecommendationRequest) -> dict[str, object]:
    vibe = request.vibe.strip()
    if not vibe:
        raise HTTPException(status_code=422, detail="Enter a scent mood first.")
    try:
        return recommend_for_web(vibe, request.count)
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
