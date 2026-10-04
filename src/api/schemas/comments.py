from pydantic import BaseModel


class CommentItem(BaseModel):
    comment_id: int
    user_id: int
    text: str


class CommentAnalysisRequest(BaseModel):
    video_id: int
    comments: list[CommentItem]


class CommentsAnalysisResponse(BaseModel):
    overall_sentiment: str
    pros: list[str]
    cons: list[str]
    spam_comments: list[int]
