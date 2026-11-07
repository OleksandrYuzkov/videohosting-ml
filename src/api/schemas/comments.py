from typing import Literal

from pydantic import BaseModel, Field


class TopicLLM(BaseModel):
    title: str
    sentiment: Literal["positive", "negative", "mixed"]
    percentage: float
    key_takeaway: str


class AudienceReportLLM(BaseModel):
    executive_summary: str
    topics: list[TopicLLM]


class TopicItem(TopicLLM):
    comment_ids: list[str | int] = Field(default_factory=list)


class AudienceReport(AudienceReportLLM):
    topics: list[TopicItem]


class CommentItem(BaseModel):
    comment_id: int
    author: str = Field(
        default="anonymous",
        description="Author of the comment, defaulting to 'anonymous' if not provided",
    )
    text: str
    votes: int = 0


class CommentAnalysisRequest(BaseModel):
    video_id: int
    video_title: str
    channel_name: str
    target_language: str = Field(
        default="English", description="Target language for the report"
    )
    comments: list[CommentItem]
