import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.schemas.comments import AudienceReport, CommentAnalysisRequest
from src.pipelines.clean_comments import clean_comments_pipeline
from src.pipelines.sentiment_analysis import analyse_sentiment_pipeline

router = APIRouter(prefix="/api/v1/comments", tags=["Comments"])


@router.post("/analyze", response_model=AudienceReport)
def analyze_comments(request: CommentAnalysisRequest):

    df = pd.DataFrame([c.model_dump() for c in request.comments])
    df = clean_comments_pipeline(df)

    if len(df) < 15:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient comments for cluster analysis: minimum 15 required, but only {len(df)} remaining after filtering.",
        )

    report = analyse_sentiment_pipeline(
        df=df,
        video_title=request.video_title,
        channel_name=request.channel_name,
        target_language=request.target_language,
    )

    return report
