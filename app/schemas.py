"""프론트엔드 ↔ 백엔드 API 계약 모델입니다. 수정하지 마세요."""
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class TraceEntry(BaseModel):
    node: str
    ms: int


class ChatResponse(BaseModel):
    answer: str = ""
    trace: list[TraceEntry] = Field(default_factory=list)
    error: str | None = None


class TeamSummary(BaseModel):
    id: str
    number: int
    name: str
    description: str = ""
    examples: list[str] = Field(default_factory=list)
    status: str            # ready | not_implemented | error
    error: str | None = None


class TeamListResponse(BaseModel):
    teams: list[TeamSummary]
