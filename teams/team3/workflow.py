"""3조 워크플로우

┌────────────────────────────────────────────────────────────┐
│  이 파일이 여러분이 채워야 할 유일한 코드 파일입니다.       │
│  teams/team3/ 폴더 밖의 파일은 절대 수정하지 마세요.      │
│  (다른 조와 충돌이 납니다)                                  │
└────────────────────────────────────────────────────────────┘

작업 순서
  1. TEAM_INFO 를 우리 조 주제에 맞게 바꿉니다.
  2. MyState 에 노드끼리 주고받을 필드를 추가합니다.
  3. 노드 함수를 하나씩 만듭니다. (state 를 받아 바뀐 값만 dict 로 반환)
  4. build_graph() 에서 노드와 엣지를 연결합니다.
  5. 마지막 노드에서 answer 를 반드시 채웁니다. 이게 화면에 보이는 답변입니다.
  6. python scripts/selfcheck.py team3 으로 확인한 뒤 커밋하세요.

막히면 teams/team0/workflow.py (여행지 추천 예제) 를 열어보세요.

터미널에서 이 파일만 바로 실행해 볼 수 있습니다. (화면 없이 디버깅할 때 편합니다)

    python teams/team3/workflow.py "테스트할 질문"
"""
from __future__ import annotations

import sys
from pathlib import Path

# 이 파일을 직접 실행할 때도 app/ 을 찾을 수 있도록 최상위 폴더를 경로에 추가합니다.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph

from app.contract import BaseGraphState
from app.llm import get_llm
from teams.team3.prompts import FINAL_NODE_SYSTEM, FIRST_NODE_SYSTEM

# ── 1단계: 우리 조 정보 ──────────────────────────────────────────
# 화면의 탭 이름과 예시 질문으로 쓰입니다. 여기에 작성하시면 됩니다.
TEAM_INFO = {
    "name": "3조",       # 예: "3조 · 레시피 추천 봇"
    "description": "",      # 한 줄 소개를 적어주세요
    "examples": [],         # 예시 질문 3개를 적어주세요
}


# ── 2단계: 상태 정의 ────────────────────────────────────────────
# BaseGraphState 에는 user_input / messages / answer 가 이미 들어있습니다.
# 노드끼리 주고받을 값을 여기에 추가하시면 됩니다.
class MyState(BaseGraphState):
    pass
    # 예시:
    # keywords: list[str]
    # draft: str


def _ask(system: str, user: str, temperature: float = 0.3) -> str:
    """LLM 을 한 번 호출하는 도우미입니다. 그대로 쓰셔도 됩니다."""
    llm = get_llm(temperature=temperature)
    result = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    return (result.content or "").strip()


# ── 3단계: 노드 함수 ────────────────────────────────────────────
# 노드는 state 를 받아서, 바꾸고 싶은 값만 dict 로 반환합니다.
def first_node(state: MyState) -> dict:
    # 여기에 작성하시면 됩니다.
    # 예: return {"keywords": _ask(FIRST_NODE_SYSTEM, state["user_input"]).split(",")}
    return {}


def final_node(state: MyState) -> dict:
    # 마지막 노드에서는 answer 를 반드시 채워주세요. 화면에 보이는 값입니다.
    # 여기에 작성하시면 됩니다.
    return {"answer": _ask(FINAL_NODE_SYSTEM, state["user_input"])}


# ── 4단계: 그래프 조립 ──────────────────────────────────────────
def build_graph():
    # 개발을 시작하면 아래 raise 줄을 지우세요.
    raise NotImplementedError("아직 개발 중입니다. build_graph() 를 완성해주세요.")

    builder = StateGraph(MyState)

    builder.add_node("first_node", first_node)
    builder.add_node("final_node", final_node)

    builder.add_edge(START, "first_node")
    builder.add_edge("first_node", "final_node")
    builder.add_edge("final_node", END)

    # 조건 분기를 쓰고 싶다면 teams/team0/workflow.py 의
    # add_conditional_edges 부분을 참고하세요.
    return builder.compile()


# ── 터미널에서 바로 실행하기 ─────────────────────────────────────
# 화면을 띄우지 않고 노드가 어떤 값을 만들어내는지 하나씩 찍어보고 싶을 때 씁니다.
# 고칠 필요 없습니다. 그대로 두고 아래처럼 실행하세요.
#
#     python teams/team3/workflow.py "테스트할 질문"
#
if __name__ == "__main__":
    from app.contract import make_initial_state
    from app.llm import LLMConfigError

    message = " ".join(sys.argv[1:]) or "테스트 질문"
    print(f"입력: {message}\n")

    answer = ""
    try:
        graph = build_graph()
        for chunk in graph.stream(make_initial_state(message), stream_mode="updates"):
            for node, update in chunk.items():
                print(f"── {node}")
                for key, value in (update or {}).items():
                    text = str(value).replace("\n", " ")
                    print(f"   {key} = {text[:160]}{'…' if len(text) > 160 else ''}")
                if isinstance(update, dict) and update.get("answer"):
                    answer = update["answer"]
                print()
    except (NotImplementedError, LLMConfigError) as exc:
        print(f"[안내] {exc}")
        raise SystemExit(1)

    print("=" * 60)
    print(answer)
