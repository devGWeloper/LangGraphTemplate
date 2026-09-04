"""LLM 클라이언트 팩토리입니다. 이 파일은 수정하지 마세요.

조원은 아래처럼 가져다 쓰기만 하면 됩니다.

    from app.llm import get_llm
    llm = get_llm(temperature=0.2)
    result = llm.invoke("안녕하세요")
"""
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

_REQUIRED = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")


class LLMConfigError(RuntimeError):
    """LLM 접속 환경변수가 설정되지 않았을 때 발생합니다."""


def get_llm(temperature: float = 0.3, model: str | None = None) -> ChatOpenAI:
    """.env 값으로 OpenAI 호환 채팅 모델 클라이언트를 만들어 돌려줍니다."""
    missing = [key for key in _REQUIRED if not os.getenv(key)]
    if missing:
        raise LLMConfigError(
            f".env 파일에 다음 값이 비어 있습니다: {', '.join(missing)}\n"
            f".env.example 을 복사해 .env 를 만들고 값을 채워주세요."
        )
    return ChatOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        model=model or os.environ["LLM_MODEL"],
        temperature=temperature,
    )
