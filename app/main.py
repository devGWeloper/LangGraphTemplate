"""챌린지 플랫폼 서버입니다. 이 파일은 수정하지 마세요."""
from __future__ import annotations

import time
import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import discovery
from app.contract import make_initial_state
from app.discovery import STATUS_READY, TeamEntry, get_graph
from app.schemas import (
    ChatRequest,
    ChatResponse,
    TeamListResponse,
    TeamSummary,
    TraceEntry,
)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(title="AI 챌린지 플랫폼")

_TEAM_CACHE: list[TeamEntry] = []


def _teams() -> list[TeamEntry]:
    if not _TEAM_CACHE:
        _TEAM_CACHE.extend(discovery.discover_teams())
    return _TEAM_CACHE


def _find(team_id: str) -> TeamEntry | None:
    return next((entry for entry in _teams() if entry.id == team_id), None)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/teams", response_model=TeamListResponse)
def list_teams() -> TeamListResponse:
    return TeamListResponse(teams=[
        TeamSummary(
            id=e.id, number=e.number, name=e.name, description=e.description,
            examples=e.examples, status=e.status, error=e.error,
        )
        for e in _teams()
    ])


async def run_team_graph(entry: TeamEntry, message: str, history: list[dict]) -> ChatResponse:
    """조의 그래프를 실행하고 답변과 노드 실행 기록을 모아 돌려줍니다."""
    if entry.status != STATUS_READY:
        return ChatResponse(error=entry.error or f"{entry.name} 은 아직 준비되지 않았습니다.")

    state = make_initial_state(message, history)
    trace: list[TraceEntry] = []
    answer = ""
    try:
        graph = get_graph(entry)
        started = time.perf_counter()
        async for chunk in graph.astream(state, stream_mode="updates"):
            for node, update in chunk.items():
                now = time.perf_counter()
                trace.append(TraceEntry(node=node, ms=int((now - started) * 1000)))
                started = now
                if isinstance(update, dict) and update.get("answer"):
                    answer = update["answer"]
    except Exception as exc:
        return ChatResponse(
            trace=trace,
            error=f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc(limit=3)}",
        )

    if not answer:
        return ChatResponse(
            trace=trace,
            error="그래프가 끝났지만 answer 값이 비어 있습니다. 마지막 노드에서 answer 를 채워주세요.",
        )
    return ChatResponse(answer=answer, trace=trace)


@app.post("/api/chat/{team_id}", response_model=ChatResponse)
async def chat(team_id: str, request: ChatRequest) -> ChatResponse:
    entry = _find(team_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"{team_id} 를 찾을 수 없습니다.")
    history = [m.model_dump() for m in request.history]
    return await run_team_graph(entry, request.message, history)


# 빌드된 프론트엔드를 같은 포트에서 서빙합니다. (frontend/dist 가 있을 때만)
if (FRONTEND_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")
