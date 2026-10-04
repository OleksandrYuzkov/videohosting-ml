from pydantic import BaseModel


class MomentSearchRequest(BaseModel):
    query: str
    video_id: int | None = None
    limit: int = 10


class MomentSearchResult(BaseModel):
    video_id: int
    start_time: float
    end_time: float
    score: float


class MomentSearchResponse(BaseModel):
    results: list[MomentSearchResult]
