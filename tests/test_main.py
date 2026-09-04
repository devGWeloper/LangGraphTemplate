import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.discovery import STATUS_NOT_IMPLEMENTED, STATUS_READY, TeamEntry
from app.main import app


class FakeGraph:
    """astream 만 흉내내는 가짜 그래프입니다."""

    def __init__(self, answer="안녕하세요", nodes=("plan", "reply"), raises=None):
        self.answer = answer
        self.nodes = nodes
        self.raises = raises

    async def astream(self, state, stream_mode="updates"):
        if self.raises:
            raise self.raises
        for node in self.nodes:
            yield {node: {"answer": self.answer}}


def _entry(number=0, status=STATUS_READY, graph=None, error=None):
    entry = TeamEntry(id=f"team{number}", number=number, name=f"{number}조",
                      status=status, error=error)
    entry._graph = graph
    return entry


@pytest.fixture
def client():
    http = TestClient(app)

    def set_teams(entries):
        main_module._TEAM_CACHE.clear()
        main_module._TEAM_CACHE.extend(entries)

    yield http, set_teams
    main_module._TEAM_CACHE.clear()


def test_health(client):
    http, _ = client
    assert http.get("/api/health").json() == {"status": "ok"}


def test_list_teams_returns_summaries(client):
    http, set_teams = client
    set_teams([_entry(0, graph=FakeGraph()), _entry(1, status=STATUS_NOT_IMPLEMENTED)])
    body = http.get("/api/teams").json()
    assert [t["id"] for t in body["teams"]] == ["team0", "team1"]
    assert body["teams"][0]["status"] == STATUS_READY
    assert body["teams"][1]["status"] == STATUS_NOT_IMPLEMENTED


def test_chat_returns_answer_and_trace(client):
    http, set_teams = client
    set_teams([_entry(0, graph=FakeGraph(answer="부산 추천드립니다"))])
    body = http.post("/api/chat/team0", json={"message": "부산", "history": []}).json()
    assert body["answer"] == "부산 추천드립니다"
    assert [t["node"] for t in body["trace"]] == ["plan", "reply"]
    assert body["error"] is None


def test_chat_on_unknown_team_returns_404(client):
    http, set_teams = client
    set_teams([_entry(0, graph=FakeGraph())])
    assert http.post("/api/chat/team9", json={"message": "안녕"}).status_code == 404


def test_chat_on_not_implemented_team_returns_error_field(client):
    http, set_teams = client
    set_teams([_entry(1, status=STATUS_NOT_IMPLEMENTED, error="아직 구현되지 않았습니다.")])
    body = http.post("/api/chat/team1", json={"message": "안녕"}).json()
    assert body["answer"] == ""
    assert "구현" in body["error"]


def test_chat_wraps_team_exception_into_error_field(client):
    http, set_teams = client
    set_teams([_entry(0, graph=FakeGraph(raises=ValueError("조원 코드 버그")))])
    resp = http.post("/api/chat/team0", json={"message": "안녕"})
    assert resp.status_code == 200
    assert "조원 코드 버그" in resp.json()["error"]


def test_chat_reports_empty_answer(client):
    http, set_teams = client
    set_teams([_entry(0, graph=FakeGraph(answer=""))])
    assert "answer" in http.post("/api/chat/team0", json={"message": "안녕"}).json()["error"]


def test_chat_passes_history_into_state(client):
    http, set_teams = client
    captured = {}

    class RecordingGraph(FakeGraph):
        async def astream(self, state, stream_mode="updates"):
            captured.update(state)
            yield {"reply": {"answer": "ok"}}

    set_teams([_entry(0, graph=RecordingGraph())])
    http.post("/api/chat/team0", json={
        "message": "두 번째 질문",
        "history": [{"role": "user", "content": "첫 질문"}],
    })
    assert captured["user_input"] == "두 번째 질문"
    assert captured["messages"] == [{"role": "user", "content": "첫 질문"}]
