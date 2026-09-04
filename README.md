# 제조AX서비스1팀 AI 챌린지

LangGraph 로 나만의 MultiAgent 를 만들어보는 챌린지 플랫폼입니다.

각 조가 자유 주제로 에이전트를 개발하면, 하나의 화면에 조별 탭으로 붙어서
바로 대화해볼 수 있습니다. **화면은 이미 다 만들어져 있습니다. 여러분은 백엔드만 만들면 됩니다.**

---

## 여러분이 손대는 곳

```
LangGraphTemplate/
├─ app/                    ← 공용 백엔드. 수정하지 마세요
├─ frontend/               ← 공용 화면. 수정하지 마세요
├─ docs/                   ← 안내 문서
├─ scripts/selfcheck.py    ← 제출 전 자가 점검
└─ teams/
   ├─ team0/               ← 📖 예제 (여행지 추천). 먼저 읽어보세요
   │  ├─ workflow.py
   │  ├─ prompts.py
   │  └─ README.md         ← 이렇게 쓰면 됩니다 (모범답안)
   │
   └─ team3/               ← ✏️ 여러분 조 폴더. 여기만 채우면 됩니다
      ├─ workflow.py       ← 그래프 코드
      ├─ prompts.py        ← 프롬프트
      └─ README.md         ← 산출물 (평가 대상)
```

> ⚠️ **가장 중요한 규칙: `teams/teamN/` 폴더 밖의 파일은 절대 수정하지 마세요.**
> 나중에 모든 조의 작업을 하나로 합칠 때 충돌이 납니다.
> 여러분 폴더 안에서만 작업하면 충돌은 구조적으로 발생하지 않습니다.

---

## 시작하기

1. **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** 를 따라 환경을 만듭니다. (파이썬 설치부터 단계별로 있습니다)
2. `python run.py` 로 서버를 켜고 http://localhost:8021 에 접속합니다.
3. **0조 탭**에서 여행지 추천 예제와 먼저 대화해봅니다.
4. `teams/team0/workflow.py` 를 열어 어떻게 만들어졌는지 읽어봅니다.
5. 우리 조 폴더의 `workflow.py` 를 채우기 시작합니다.

---

## 개발 5단계

`teams/teamN/workflow.py` 안에 안내 주석이 단계별로 달려 있습니다.

### 1️⃣ 우리 조 정보 쓰기

```python
TEAM_INFO = {
    "name": "3조 · 레시피 추천 봇",
    "description": "냉장고 재료로 만들 수 있는 요리를 추천합니다.",
    "examples": ["계란이랑 양파밖에 없어", "매운 거 먹고 싶어", "10분 야식 알려줘"],
}
```

### 2️⃣ 상태(State) 정의하기

노드끼리 주고받을 값을 정합니다. `user_input` / `messages` / `answer` 는 이미 들어있습니다.

```python
class MyState(BaseGraphState):
    ingredients: list[str]
    recipes: str
```

### 3️⃣ 노드 함수 만들기

노드는 `state` 를 받아서 **바꾸고 싶은 값만** dict 로 반환합니다.

```python
def extract_ingredients(state: MyState) -> dict:
    text = _ask(EXTRACT_SYSTEM, state["user_input"])
    return {"ingredients": text.split(",")}
```

### 4️⃣ 그래프 조립하기

```python
builder.add_node("extract_ingredients", extract_ingredients)
builder.add_edge(START, "extract_ingredients")
```

조건 분기가 필요하면 `teams/team0/workflow.py` 의 `add_conditional_edges` 부분을 보세요.

> 🔑 **마지막 노드에서 `answer` 를 반드시 채워주세요.** 화면에 보이는 값입니다.

### 5️⃣ 자가 점검하고 커밋

```cmd
python scripts\selfcheck.py team3
```

`[통과]` 가 나오면 제출 준비 완료입니다.

---

## 디버깅하는 두 가지 방법

### 1. 터미널에서 파일 하나만 실행하기

화면을 띄우지 않고 빠르게 확인할 때 씁니다.

```cmd
python teams\team3\workflow.py "테스트할 질문"
```

노드가 순서대로 실행되면서 **각 노드가 만든 값**이 그대로 찍힙니다.

```
입력: 계란이랑 양파밖에 없어

── extract_ingredients
   ingredients = ['계란', '양파']

── suggest_recipe
   answer = 계란말이를 추천드려요. 양파를 잘게 다져…

============================================================
계란말이를 추천드려요. 양파를 잘게 다져…
```

어느 노드에서 값이 이상해지는지 한눈에 보입니다.
`print()` 를 노드 안에 직접 넣어가며 확인하셔도 됩니다.

### 2. 화면에서 확인하기

```cmd
python run.py
```

http://localhost:8021 에서 우리 조 탭을 열고 대화해봅니다.
답변 아래에 **실제로 실행된 노드와 소요 시간**이 표시되니, 의도한 경로로 흘렀는지 바로 확인할 수 있습니다.

```
analyze_intent 812ms —— recommend 1.5s —— build_itinerary 2.2s
```

코드에서 오류가 나면 화면에 오류 내용이 그대로 뜹니다. 서버는 죽지 않고, 다른 조에도 영향이 없습니다.

---

## 제출물 3개

| 파일 | 내용 |
|---|---|
| `teams/teamN/workflow.py` | 그래프 코드 |
| `teams/teamN/prompts.py` | 프롬프트 |
| `teams/teamN/README.md` | **산출물 문서 — 이 문서로 평가합니다** |

`README.md` 는 템플릿이 이미 들어있습니다. 세 장을 채우시면 됩니다.

1. **LangGraph 워크플로우 설계** — State, 노드, 엣지, mermaid 다이어그램, 그렇게 설계한 이유
2. **프롬프트 엔지니어링** — 노드별 프롬프트 전문, 설계 의도, 개선 전/후
3. **실행 결과 & 회고** — 실행 예시(실패 케이스 포함), 잘 된 점과 한계, 역할 분담, 배운 점

**[teams/team0/README.md](teams/team0/README.md) 가 이 세 장을 다 채운 모범답안입니다.** 먼저 읽어보세요.

---

## 규칙

- ✅ `teams/teamN/` 폴더 안에서만 작업합니다.
- ✅ 패키지를 추가해야 하면 `requirements.txt` **맨 아래 `# --- 조별 추가 ---` 구역에만** 한 줄씩 적습니다.
- ❌ `.env` 파일은 커밋하지 않습니다. (API 키가 들어갑니다)
- ❌ `app/`, `frontend/`, `docs/` 는 수정하지 않습니다.

커밋 전에 확인해보세요.

```cmd
git diff --name-only
```

`teams/teamN/` 밖의 파일이 나오면 되돌려주세요.

---

## 더 읽을 것

- [환경 구축 가이드](docs/SETUP_GUIDE.md) — 설치부터 실행까지
- [API 계약](docs/API_CONTRACT.md) — `TEAM_INFO`, `build_graph()`, State, 응답 형식
- [0조 예제 코드](teams/team0/workflow.py) — 4노드 + 조건분기 MultiAgent
- [0조 산출물 문서](teams/team0/README.md) — README 모범답안
