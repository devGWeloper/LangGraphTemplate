"""0조 예제 — 여행지 추천 MultiAgent

이 파일은 여러분이 참고할 "모범답안"입니다.
그래프를 어떻게 나누고, 상태를 어떻게 넘기고, 조건 분기를 어떻게 거는지 보세요.

그래프 구조
    analyze_intent ─┬─ (정보 부족) → ask_clarify ──────────────→ END
                    └─ (정보 충분) → recommend → build_itinerary → END
"""
from __future__ import annotations

import json

from langgraph.graph import END, START, StateGraph

from app.contract import BaseGraphState
from app.llm import get_llm
from teams.team0.prompts import (
    ANALYZE_INTENT_SYSTEM,
    ASK_CLARIFY_SYSTEM,
    BUILD_ITINERARY_SYSTEM,
    RECOMMEND_SYSTEM,
)

TEAM_INFO = {
    "name": "0조 · 여행지 추천 플래너",
    "description": "가고 싶은 지역과 일정을 알려주면 후보지를 고르고 일자별 일정표까지 만들어 드립니다.",
    "examples": [
        "친구랑 부산 2박 3일 가려고 하는데 맛집 위주로 추천해줘",
        "혼자 조용히 쉴 수 있는 국내 여행지 알려줘",
        "가족이랑 제주도 3일 일정 짜줘",
    ],
}

REQUIRED_FIELDS = ("region", "days")


class TravelState(BaseGraphState):
    """0조가 사용하는 상태입니다. BaseGraphState 를 상속해 필드를 더했습니다."""

    preferences: dict   # {"region": ..., "days": ..., "companion": ..., "style": [...]}
    missing: list[str]  # 아직 모르는 필수 항목
    candidates: str     # recommend 노드가 만든 후보 목록


def _ask(system: str, user: str, temperature: float = 0.3) -> str:
    """system + user 메시지로 LLM 을 한 번 호출하고 텍스트만 뽑아옵니다."""
    llm = get_llm(temperature=temperature)
    result = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    return (result.content or "").strip()


def _history_text(messages: list[dict]) -> str:
    """이전 대화를 프롬프트에 넣기 좋은 텍스트로 만듭니다. (최근 6턴만)"""
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages[-6:])


# ── 노드 1: 의도 분석 ────────────────────────────────────────────
# 사용자 발화에서 여행 조건을 뽑아내고, 추천을 진행할 만큼 정보가 모였는지 판단합니다.
def analyze_intent(state: TravelState) -> dict:
    user = (
        f"이전 대화:\n{_history_text(state['messages'])}\n\n"
        f"이번 발화:\n{state['user_input']}"
    )
    raw = _ask(ANALYZE_INTENT_SYSTEM, user, temperature=0.0)

    # LLM 이 JSON 앞뒤에 설명 문장을 붙일 수 있으니 방어적으로 파싱합니다.
    try:
        preferences = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError):
        preferences = {"region": None, "days": None, "companion": None, "style": []}

    missing = [f for f in REQUIRED_FIELDS if not preferences.get(f)]
    return {"preferences": preferences, "missing": missing}


# ── 분기: 정보가 충분한가? ───────────────────────────────────────
# 이 함수의 반환값이 다음에 실행할 노드 이름이 됩니다.
def route_after_intent(state: TravelState) -> str:
    return "ask_clarify" if state["missing"] else "recommend"


# ── 노드 2: 되묻기 ──────────────────────────────────────────────
def ask_clarify(state: TravelState) -> dict:
    user = (
        f"지금까지 파악한 정보: {state['preferences']}\n"
        f"아직 모르는 항목: {', '.join(state['missing'])}"
    )
    return {"answer": _ask(ASK_CLARIFY_SYSTEM, user, temperature=0.5)}


# ── 노드 3: 후보 추천 ───────────────────────────────────────────
def recommend(state: TravelState) -> dict:
    prefs = state["preferences"]
    style = ", ".join(prefs.get("style") or []) or "없음"
    user = (
        f"지역: {prefs.get('region')}\n"
        f"일수: {prefs.get('days')}\n"
        f"동행: {prefs.get('companion') or '미상'}\n"
        f"취향: {style}"
    )
    return {"candidates": _ask(RECOMMEND_SYSTEM, user, temperature=0.7)}


# ── 노드 4: 일정 구성 (최종 답변) ────────────────────────────────
def build_itinerary(state: TravelState) -> dict:
    user = f"조건: {state['preferences']}\n\n후보 목록:\n{state['candidates']}"
    return {"answer": _ask(BUILD_ITINERARY_SYSTEM, user, temperature=0.6)}


def build_graph():
    """노드와 엣지를 연결해 그래프를 완성합니다."""
    builder = StateGraph(TravelState)

    builder.add_node("analyze_intent", analyze_intent)
    builder.add_node("ask_clarify", ask_clarify)
    builder.add_node("recommend", recommend)
    builder.add_node("build_itinerary", build_itinerary)

    builder.add_edge(START, "analyze_intent")
    builder.add_conditional_edges(
        "analyze_intent",
        route_after_intent,
        {"ask_clarify": "ask_clarify", "recommend": "recommend"},
    )
    builder.add_edge("ask_clarify", END)
    builder.add_edge("recommend", "build_itinerary")
    builder.add_edge("build_itinerary", END)

    return builder.compile()
