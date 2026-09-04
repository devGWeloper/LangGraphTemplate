# LangGraph 챌린지 플랫폼 — 설계 문서

작성일: 2026-09-04
저장소: https://github.com/devGWeloper/LangGraphTemplate (단일 저장소, 조별 브랜치 운영)

## 1. 목적

팀원의 LangGraph/LangChain 개발, MultiAgent 워크플로우 설계, 프롬프트 엔지니어링 역량을
끌어올리기 위한 챌린지 플랫폼이다. 조원은 자유 주제로 MultiAgent 백엔드를 개발해 제출하고,
리드는 조별 README.md 하나로 산출물을 평가한다.

- 0조: 템플릿 겸 모범답안. 여행지 추천 MultiAgent 예제가 실제로 동작한다.
- 1~7조: 각 조가 자기 폴더만 채운다.
- 조별 브랜치를 최종적으로 모두 merge하면 하나의 앱에서 8개 채팅 탭이 뜬다.

## 2. 설계 원칙

1. **조원은 `teams/teamN/` 밖의 파일을 절대 수정하지 않는다.** merge 충돌을 구조적으로 0으로 만든다.
2. **한 조가 깨져도 전체가 죽지 않는다.** 조별 모듈 import 실패는 격리되어 해당 탭만 비활성화된다.
3. **대상은 초심자다.** 파이썬 설치부터 기동까지 단계별 문서를 제공하고, 코드에는 안내 주석을 충분히 넣는다.
4. **배관은 공용 앱이 처리한다.** 채팅 히스토리, LLM 클라이언트 생성, 노드 실행 추적은 조원이 신경 쓰지 않는다.
5. 소스코드와 팀원용 문서 어디에도 사내 환경을 암시하는 워딩을 넣지 않는다. `LEAD_GUIDE.md`만 예외다.

## 3. 디렉토리 구조

```
LangGraphTemplate/
├─ app/                        # 공용 백엔드 (조원 수정 금지)
│   ├─ __init__.py
│   ├─ main.py                 # FastAPI 앱, 정적 서빙, API 라우트
│   ├─ discovery.py            # teams/* 스캔 → workflow.py 동적 import
│   ├─ contract.py             # BaseGraphState 등 조원이 import 하는 공용 타입
│   ├─ llm.py                  # get_llm() — OpenAI 호환 클라이언트 팩토리
│   └─ schemas.py              # 요청/응답 Pydantic 모델
├─ teams/
│   ├─ __init__.py
│   ├─ team0/                  # 예제: 여행지 추천 MultiAgent
│   │   ├─ __init__.py
│   │   ├─ workflow.py
│   │   ├─ prompts.py
│   │   └─ README.md           # 템플릿을 100% 채운 모범답안
│   └─ team1/ … team7/         # 빈 뼈대 (동일 파일 구성, TODO 주석)
├─ frontend/                   # React + Vite (조원 수정 금지)
│   ├─ index.html
│   ├─ package.json
│   ├─ vite.config.js
│   └─ src/
├─ docs/
│   ├─ SETUP_GUIDE.md          # 초심자용 환경 구축 → 기동
│   └─ API_CONTRACT.md         # 프론트 ↔ 백엔드 계약
├─ scripts/
│   └─ selfcheck.py            # 조원이 제출 전 스스로 계약 준수 검사
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ README.md                   # 팀원용 전체 안내
└─ LEAD_GUIDE.md               # 리드 전용 운영 가이드
```

## 4. 조별 모듈 계약

`teams/teamN/workflow.py`는 다음 두 가지를 반드시 export 한다.

```python
TEAM_INFO = {
    "name": "3조 · 레시피 추천 봇",
    "description": "냉장고 재료로 만들 수 있는 요리를 추천합니다.",
    "examples": ["계란이랑 양파밖에 없어", "매운 거 먹고 싶어"],
}

def build_graph():
    """컴파일된 LangGraph 그래프를 반환한다."""
```

상태는 `app/contract.py`의 `BaseGraphState`를 상속해 필드를 추가한다.

```python
class BaseGraphState(TypedDict):
    user_input: str                 # 이번 턴 사용자 입력
    messages: list[dict]            # 이전 대화 이력 [{role, content}]
    answer: str                     # 최종 답변 (반드시 채울 것)
```

- 공용 앱은 `{"user_input": ..., "messages": ..., "answer": ""}`로 그래프를 실행하고
  최종 상태의 `answer`를 응답으로 돌려준다.
- `answer`가 비어 있으면 공용 앱이 명확한 오류 메시지를 반환한다.

### 디스커버리 규칙

- `teams/team{숫자}` 형태의 폴더를 스캔한다. 번호 오름차순으로 탭을 정렬한다.
- import 성공 + `build_graph` 존재 → 상태 `ready`
- `NotImplementedError` 또는 `build_graph` 부재 → 상태 `not_implemented`
- 그 외 예외 → 상태 `error` (예외 메시지를 탭에 노출해 조원이 디버깅 가능)
- `TEAM_INFO`가 없으면 폴더명에서 "N조"를 유추해 fallback으로 사용한다.
- 그래프는 최초 요청 시 1회 빌드하고 캐시한다.

## 5. API

기동은 단일 포트 8021. uvicorn이 `frontend/dist`의 빌드 결과를 정적 서빙한다.

### `GET /api/teams`

```json
{"teams": [
  {"id": "team0", "number": 0, "name": "0조 · 여행지 추천", "description": "...",
   "examples": ["..."], "status": "ready", "error": null}
]}
```

### `POST /api/chat/{team_id}`

요청:
```json
{"message": "부산 2박3일 추천해줘", "history": [{"role": "user", "content": "..."}]}
```

응답:
```json
{"answer": "...", "trace": [{"node": "analyze_intent", "ms": 812}], "error": null}
```

- `trace`는 공용 앱이 `graph.astream()`으로 자동 수집한다. 조원 코드는 아무 것도 하지 않아도 된다.
- 조원 코드에서 예외가 나면 500이 아니라 200 + `error` 필드로 돌려 UI가 친절하게 표시한다.

## 6. LLM 연동

`app/llm.py`의 `get_llm(temperature=..., model=...)` 하나만 제공한다.
`langchain-openai`의 `ChatOpenAI`를 OpenAI 호환 엔드포인트로 구성한다.

`.env.example`:
```
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
```

실제 값은 저장소에 절대 넣지 않는다. 값이 비어 있으면 기동은 되되 채팅 시
"환경변수를 설정해주세요"라는 안내 메시지를 반환한다.

## 7. 0조 예제 — 여행지 추천 (4노드 + 조건분기)

```
analyze_intent ─┬─ (정보 부족) → ask_clarify ──────────────→ END
                └─ (정보 충분) → recommend → build_itinerary → END
```

| 노드 | 역할 |
|---|---|
| `analyze_intent` | 사용자 발화에서 지역/기간/동행/취향을 추출하고 충분성을 판단 |
| `ask_clarify` | 부족한 정보를 되묻는 질문 생성 |
| `recommend` | 후보 여행지 3곳을 근거와 함께 생성 |
| `build_itinerary` | 후보를 일자별 일정으로 구성하고 최종 답변 작성 |

State: `user_input, messages, answer, preferences, missing, candidates, itinerary`

프롬프트는 `prompts.py`로 분리해 프롬프트 엔지니어링 대상임을 드러낸다.

## 8. 조별 README 템플릿 (핵심 산출물)

Bitbucket에서 스크롤만으로 평가가 끝나도록 구성한다.

```
# {N}조 — {프로젝트명}
한 줄 소개 / 예시 질문 3개

## 1. LangGraph 워크플로우 설계
  1.1 State 스키마          표: 필드 | 타입 | 설명
  1.2 노드 구성             표: 노드 | 역할 | 입력 | 출력
  1.3 엣지 & 조건 분기      표: 출발 | 조건 | 도착
  1.4 워크플로우 다이어그램  mermaid 필수, png 선택
  1.5 이 구조로 설계한 이유

## 2. 프롬프트 엔지니어링
  노드별: 최종 System Prompt 전문 / 설계 의도 /
          개선 전 → 후 최소 1회 + 무엇이 달라졌는지

## 3. 실행 결과 & 회고
  3.1 실행 예시 2건 이상 (실패·엣지 케이스 1건 필수)
  3.2 잘 된 점 / 한계 / 개선 아이디어
  3.3 역할 분담
  3.4 배운 점

제출 체크리스트 (체크박스 8개)
```

주제·기획 정의 섹션은 리드가 0조에서 별도로 정리하므로 조별 문서에서는 제외한다.

## 9. 프론트엔드

- React + Vite. 조원은 수정하지 않는다.
- 메인에 "제조AX서비스1팀 AI 챌린지" 히어로 문구.
- 8개 탭 + 채팅 화면. 차분한 다크 베이스에 절제된 단일 accent 색.
  과한 그라데이션·혼합색 데코레이션은 배제한다.
- 움직임은 마이크로 인터랙션으로 제한한다: 탭 전환, 메시지 등장, 노드 진행 배지.
- `not_implemented` / `error` 탭은 채팅 입력을 잠그고 안내 카드를 보여준다.
- 개발 시에는 Vite dev 서버(5173)가 `/api`를 8021로 프록시한다.

## 10. 의존성

루트 `requirements.txt` 하나로 통일한다. 공통 패키지를 넉넉히 미리 포함해 대부분의 조가
파일을 수정할 일이 없게 한다. 추가가 필요하면 파일 맨 아래 `# --- 조별 추가 ---`
구역에만 append 하도록 규칙을 문서화한다. 충돌이 나더라도 "양쪽 다 살리기"로 해결된다.

## 11. 테스트

pytest로 공용 앱만 검증한다. 조원 코드는 테스트 대상이 아니다.

- `discovery`: 정상 조 인식, `not_implemented` 처리, import 오류 격리, 번호 정렬
- `main`: `/api/teams` 응답 형태, `/api/chat` 정상/오류 경로, 존재하지 않는 team_id
- `contract`: `answer` 미설정 시 오류 처리

추가로 `scripts/selfcheck.py`를 제공해 조원이 제출 전 자기 폴더의 계약 준수를 스스로 확인한다.

## 12. 산출 문서

| 파일 | 대상 | 비고 |
|---|---|---|
| `README.md` | 팀원 | 전체 안내, 규칙, 빠른 시작 |
| `docs/SETUP_GUIDE.md` | 팀원 | 파이썬 설치 → venv → pip → 기동 |
| `docs/API_CONTRACT.md` | 팀원 | 계약 상세 |
| `teams/teamN/README.md` | 팀원 | 평가 산출물 템플릿 |
| `teams/team0/README.md` | 팀원 | 모범답안 |
| `LEAD_GUIDE.md` | 리드 | 브랜치 운영, merge, 평가 배점 |
