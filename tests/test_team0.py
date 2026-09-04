import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from teams.team0 import workflow as team0


class FakeLLM:
    """LLM 호출을 흉내내는 가짜 객체입니다. 네트워크 없이 그래프 흐름만 검증합니다."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)

        class Result:
            def __init__(self, text):
                self.content = text

        return Result(self.responses.pop(0))


def test_team_info_is_complete():
    assert team0.TEAM_INFO["name"]
    assert team0.TEAM_INFO["description"]
    assert len(team0.TEAM_INFO["examples"]) >= 3


def test_route_after_intent_asks_when_region_missing():
    assert team0.route_after_intent({"missing": ["region"]}) == "ask_clarify"


def test_route_after_intent_recommends_when_complete():
    assert team0.route_after_intent({"missing": []}) == "recommend"


def test_analyze_intent_parses_json(monkeypatch):
    fake = FakeLLM([json.dumps(
        {"region": "부산", "days": 2, "companion": "친구", "style": ["맛집"]}
    )])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.analyze_intent({"user_input": "친구랑 부산 2박", "messages": [], "answer": ""})
    assert result["preferences"]["region"] == "부산"
    assert result["missing"] == []


def test_analyze_intent_collects_missing_fields(monkeypatch):
    fake = FakeLLM([json.dumps({"region": None, "days": None, "companion": None, "style": []})])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.analyze_intent({"user_input": "여행 가고 싶어", "messages": [], "answer": ""})
    assert set(result["missing"]) == {"region", "days"}


def test_analyze_intent_survives_broken_json(monkeypatch):
    fake = FakeLLM(["죄송합니다 JSON 이 아닙니다"])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.analyze_intent({"user_input": "여행", "messages": [], "answer": ""})
    assert set(result["missing"]) == {"region", "days"}


def test_analyze_intent_extracts_json_wrapped_in_prose(monkeypatch):
    wrapped = '물론이죠! {"region": "제주", "days": 3, "companion": null, "style": []} 입니다'
    monkeypatch.setattr(team0, "get_llm", lambda **_: FakeLLM([wrapped]))
    result = team0.analyze_intent({"user_input": "제주 3일", "messages": [], "answer": ""})
    assert result["preferences"]["region"] == "제주"
    assert result["missing"] == []


def test_ask_clarify_sets_answer(monkeypatch):
    fake = FakeLLM(["어느 지역을 생각하고 계신가요?"])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.ask_clarify({
        "user_input": "여행", "messages": [], "answer": "",
        "missing": ["region"], "preferences": {},
    })
    assert result["answer"].startswith("어느 지역")


def test_recommend_sets_candidates(monkeypatch):
    fake = FakeLLM(["- 해운대\n- 감천문화마을\n- 광안리"])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.recommend({
        "user_input": "부산", "messages": [], "answer": "",
        "preferences": {"region": "부산", "days": 2, "companion": "친구", "style": ["맛집"]},
    })
    assert "해운대" in result["candidates"]


def test_build_itinerary_sets_answer(monkeypatch):
    fake = FakeLLM(["## 부산 2박 3일\nDay 1 ..."])
    monkeypatch.setattr(team0, "get_llm", lambda **_: fake)
    result = team0.build_itinerary({
        "user_input": "부산", "messages": [], "answer": "",
        "preferences": {"region": "부산", "days": 2}, "candidates": "해운대...",
    })
    assert "부산" in result["answer"]


def test_history_text_keeps_last_six_turns():
    messages = [{"role": "user", "content": str(i)} for i in range(10)]
    assert team0._history_text(messages).startswith("user: 4")


def test_build_graph_returns_runnable_graph():
    assert hasattr(team0.build_graph(), "astream")
