from fastapi import APIRouter

from src.api.schemas.comments import (
    CommentAnalysisRequest,
    CommentsAnalysisResponse,
)

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


@router.post("/analyze", response_model=CommentsAnalysisResponse)
async def analyze_comments(request: CommentAnalysisRequest):
    # Placeholder implementation for comment analysis
    return CommentsAnalysisResponse(
        overall_sentiment="positive",
        pros=["Great video!", "Very informative."],
        cons=["Too long.", "Could be more engaging."],
        spam_comments=[2, 5, 7, 10],
    )
