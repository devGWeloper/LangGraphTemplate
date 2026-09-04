# API 계약

프론트엔드와 백엔드가 주고받는 형식, 그리고 각 조가 지켜야 할 코드 계약입니다.
이 계약만 지키면 여러분의 백엔드는 화면에 그대로 붙습니다.

---

## 1. 조가 지켜야 할 코드 계약

`teams/teamN/workflow.py` 는 **딱 2가지**를 밖으로 내보내면 됩니다.

### 1.1 `TEAM_INFO`

```python
TEAM_INFO = {
    "name": "3조 · 레시피 추천 봇",          # 화면 탭에 표시될 이름
    "description": "냉장고 재료로 만들 수 있는 요리를 추천합니다.",   # 한 줄 소개
    "examples": [                            # 첫 화면에 뜨는 예시 질문 (3개 이상)
        "계란이랑 양파밖에 없어",
        "매운 거 먹고 싶어",
        "10분 안에 만들 수 있는 야식 알려줘",
    ],
}
```

| 키 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `name` | str | ✅ | 탭 이름. 없으면 폴더명에서 "N조"로 대체됩니다 |
| `description` | str | ✅ | 채팅 화면 상단 한 줄 소개 |
| `examples` | list[str] | ✅ (3개 이상) | 클릭하면 입력창에 채워지는 예시 질문 |

### 1.2 `build_graph()`

```python
def build_graph():
    builder = StateGraph(MyState)
    ...
    return builder.compile()   # 컴파일된 그래프를 반환해야 합니다
```

- 서버가 기동할 때 **한 번만** 호출하고 결과를 캐시합니다.
- 아직 개발 전이라면 `raise NotImplementedError(...)` 상태로 두세요.
  그 조의 탭은 "아직 개발 중"으로 표시되고, **다른 조에는 아무 영향이 없습니다.**

### 1.3 State — `BaseGraphState`

`app/contract.py` 에 정의되어 있습니다. 상속해서 필요한 필드를 추가하세요.

```python
from app.contract import BaseGraphState

class MyState(BaseGraphState):
    keywords: list[str]
    draft: str
```

| 필드 | 타입 | 누가 채우나 | 설명 |
|---|---|---|---|
| `user_input` | str | 서버가 채워줌 | 이번 턴 사용자 입력 |
| `messages` | list[dict] | 서버가 채워줌 | 이전 대화 이력 `[{"role": "user"\|"assistant", "content": "..."}]` |
| `answer` | str | **여러분이 채움** | 최종 답변. 그래프가 끝날 때 반드시 비어 있지 않아야 합니다 |

> ⚠️ 마지막 노드에서 `answer` 를 채우지 않으면
> "그래프가 끝났지만 answer 값이 비어 있습니다" 라는 안내가 화면에 표시됩니다.

### 1.4 LLM 호출 — `get_llm()`

```python
from app.llm import get_llm

llm = get_llm(temperature=0.3)       # 모델은 .env 의 LLM_MODEL 을 씁니다
result = llm.invoke([
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
])
text = result.content
```

접속 정보는 `.env` 에서 읽습니다. 값이 비어 있으면 `LLMConfigError` 가 발생하고,
화면에는 "환경변수를 설정해주세요" 안내가 뜹니다.

---

## 2. HTTP API

서버는 포트 **8021** 에서 동작합니다.

### 2.1 `GET /api/teams`

조 목록과 각 조의 상태를 돌려줍니다. 화면이 탭을 그릴 때 사용합니다.

**응답**

```json
{
  "teams": [
    {
      "id": "team0",
      "number": 0,
      "name": "0조 · 여행지 추천 플래너",
      "description": "가고 싶은 지역과 일정을 알려주면 ...",
      "examples": ["친구랑 부산 2박 3일 ..."],
      "status": "ready",
      "error": null
    },
    {
      "id": "team1",
      "number": 1,
      "name": "1조",
      "description": "",
      "examples": [],
      "status": "not_implemented",
      "error": "아직 개발 중입니다. build_graph() 를 완성해주세요."
    }
  ]
}
```

**`status` 값의 의미**

| 값 | 의미 | 화면 동작 |
|---|---|---|
| `ready` | 정상. 그래프가 만들어졌습니다 | 채팅 가능 |
| `not_implemented` | `build_graph()` 가 없거나 `NotImplementedError` 를 던짐 | "아직 개발 중입니다" 안내, 입력창 잠금 |
| `error` | import 실패 또는 그래프 생성 중 예외 | 에러 메시지 전문 표시, 입력창 잠금 |

### 2.2 `POST /api/chat/{team_id}`

**요청**

```json
{
  "message": "부산 2박 3일 추천해줘",
  "history": [
    {"role": "user", "content": "여행 가고 싶어"},
    {"role": "assistant", "content": "어느 지역으로 가고 싶으세요?"}
  ]
}
```

**응답**

```json
{
  "answer": "## 부산 2박 3일 코스\n\n**Day 1** ...",
  "trace": [
    {"node": "analyze_intent", "ms": 812},
    {"node": "recommend", "ms": 1503},
    {"node": "build_itinerary", "ms": 2244}
  ],
  "error": null
}
```

| 필드 | 설명 |
|---|---|
| `answer` | 최종 답변. 마크다운이 렌더링됩니다 |
| `trace` | **서버가 자동으로 수집합니다.** 실행된 노드 순서와 각 노드 소요 시간. 여러분이 할 일은 없습니다 |
| `error` | 문제가 있을 때만 채워집니다. 이때 `answer` 는 빈 문자열입니다 |

**오류 처리 방식**

- 존재하지 않는 `team_id` → HTTP **404**
- 그 외 모든 문제(조원 코드의 예외 포함) → HTTP **200** + `error` 필드에 메시지와 스택트레이스 요약
  - 한 조의 버그가 서버 전체를 죽이지 않게 하기 위함입니다. 디버깅은 화면에 뜬 메시지를 보고 하시면 됩니다.

### 2.3 `GET /api/health`

```json
{"status": "ok"}
```

---

## 3. 자동 등록 규칙

서버는 기동할 때 `teams/` 아래에서 **`team` + 숫자** 형태의 폴더를 찾습니다.

- 폴더가 있고 `workflow.py` 가 있으면 → 탭이 자동으로 생깁니다
- 번호 오름차순으로 탭이 정렬됩니다
- 등록 파일을 따로 고칠 필요가 **없습니다.** 그래서 여러 조가 동시에 작업해도 충돌이 나지 않습니다

제출 전에 자가 점검을 돌려보세요.

```bash
python scripts/selfcheck.py team3
```
