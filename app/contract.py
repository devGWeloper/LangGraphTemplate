"""조원이 import 해서 사용하는 공용 계약 타입입니다.

이 파일은 수정하지 마세요. 모든 조가 함께 사용합니다.
"""
from typing import TypedDict


class BaseGraphState(TypedDict):
    """모든 조의 LangGraph State 가 공통으로 가져야 하는 필드입니다.

    자기 조에서 필요한 필드는 이 클래스를 상속해서 자유롭게 추가하세요.

        class MyState(BaseGraphState):
            candidates: list[str]
    """

    user_input: str        # 이번 턴에 사용자가 입력한 문장
    messages: list[dict]   # 이전 대화 이력 [{"role": "user"|"assistant", "content": "..."}]
    answer: str            # 최종 답변. 그래프가 끝날 때 반드시 채워져 있어야 합니다.


def make_initial_state(user_input: str, messages: list[dict] | None = None) -> dict:
    """공용 앱이 그래프를 실행할 때 넣어주는 초기 상태입니다."""
    return {"user_input": user_input, "messages": messages or [], "answer": ""}
