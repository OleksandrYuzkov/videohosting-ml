from fastapi import APIRouter

from src.api.schemas.search import (
    MomentSearchRequest,
    MomentSearchResponse,
    MomentSearchResult,
)

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.post("/moments", response_model=MomentSearchResponse)
async def search_moments(request: MomentSearchRequest):
    return MomentSearchResponse(
        results=[
            MomentSearchResult(
                video_id=request.video_id or 1,
                start_time=14.5,
                end_time=20.0,
                score=0.92,
            )
        ]
    )
