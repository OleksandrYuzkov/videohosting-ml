from pydantic import BaseModel


class RecsysRequest(BaseModel):
    user_id: int
    novelty_weight: float = 0.5
    diversity_weight: float = 0.5
    include_topics: list[str] | None = None
    exclude_topics: list[str] | None = None
    limit: int = 10


class RecsysItem(BaseModel):
    video_id: int
    score: float


class RecsysResponse(BaseModel):
    results: list[RecsysItem]
