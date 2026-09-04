# 제조AX서비스1팀 AI 챌린지

LangGraph 로 나만의 MultiAgent 를 만들어보는 챌린지 플랫폼입니다.

각 조가 자유 주제로 에이전트를 개발하면, 하나의 화면에 조별 탭으로 붙어서
바로 대화해볼 수 있습니다. **화면은 이미 다 만들어져 있습니다. 여러분은 백엔드만 만들면 됩니다.**

---

## 여러분이 손대는 곳

```
LangGraphTemplate/
├─ run.py                  ← 백엔드 실행 (python run.py)
├─ .env                    ← 접속 정보. copy .env.example .env 로 만듭니다
├─ requirements.txt        ← 파이썬 패키지 목록
├─ app/                    ← 공용 백엔드. 수정하지 마세요
├─ frontend/               ← 공용 화면. 수정하지 마세요
├─ docs/                   ← 안내 문서
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

1. cmd 에서 프로젝트 폴더로 이동한 뒤, 처음 한 번만 설치합니다. (3~5분)

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
cd frontend
npm install
cd ..
```

2. `notepad .env` 로 열어 값 3개를 채우고 저장합니다. (값은 리드에게 받으세요)
3. cmd 창 **두 개**를 열어 하나씩 실행합니다.

```cmd
.venv\Scripts\python.exe run.py
```

```cmd
cd frontend
npm run dev
```

4. 브라우저에서 **http://localhost:5173** 을 엽니다.

각 명령이 무엇을 하는지와 오류 해결은 **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** 에 정리돼 있습니다.

화면이 뜨면:

5. **0조 탭**에서 여행지 추천 예제와 먼저 대화해봅니다.
6. `teams/team0/workflow.py` 를 열어 어떻게 만들어졌는지 읽어봅니다.
7. 우리 조 폴더의 `workflow.py` 를 채우기 시작합니다.

---

## 개발 5단계

`teams/teamN/workflow.py` 안에 안내 주석이 단계별로 달려 있습니다.
**여러분이 만들어야 할 것은 `TEAM_INFO` 와 `build_graph()` 딱 두 개입니다.**
이 둘만 있으면 서버가 알아서 탭을 만들어 붙여줍니다.

### 1️⃣ 우리 조 정보 쓰기

탭 이름과 첫 화면의 예시 질문이 됩니다.

```python
TEAM_INFO = {
    "name": "3조 · 레시피 추천 봇",                              # 탭에 표시될 이름
    "description": "냉장고 재료로 만들 수 있는 요리를 추천합니다.",   # 한 줄 소개
    "examples": [                                              # 예시 질문 3개 이상
        "계란이랑 양파밖에 없어",
        "매운 거 먹고 싶어",
        "10분 야식 알려줘",
    ],
}
```

### 2️⃣ 상태(State) 정의하기

노드끼리 주고받을 값을 정합니다. 아래 3개는 **이미 들어있습니다.**

| 필드 | 누가 채우나 | 설명 |
|---|---|---|
| `user_input` | 서버가 채워줌 | 이번에 사용자가 입력한 문장 |
| `messages` | 서버가 채워줌 | 이전 대화 이력 |
| `answer` | **여러분이 채움** | 최종 답변. 화면에 보이는 값입니다 |

여기에 필요한 걸 더하시면 됩니다.

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

LLM 을 부를 때는 `get_llm()` 을 쓰면 됩니다. 접속 정보는 `.env` 에서 알아서 읽어옵니다.

```python
from app.llm import get_llm

llm = get_llm(temperature=0.3)
result = llm.invoke([
    {"role": "system", "content": "당신은 요리 전문가입니다."},
    {"role": "user", "content": state["user_input"]},
])
text = result.content
```

### 4️⃣ 그래프 조립하기

```python
builder.add_node("extract_ingredients", extract_ingredients)
builder.add_edge(START, "extract_ingredients")
```

조건 분기가 필요하면 `teams/team0/workflow.py` 의 `add_conditional_edges` 부분을 보세요.

> 🔑 **마지막 노드에서 `answer` 를 반드시 채워주세요.** 화면에 보이는 값입니다.
> 안 채우면 "그래프가 끝났지만 answer 값이 비어 있습니다" 라는 안내가 화면에 뜹니다.

개발 전에는 `build_graph()` 가 `NotImplementedError` 를 던지도록 되어 있습니다.
그 상태에서는 탭이 "아직 개발 중"으로 표시되고, **다른 조에는 아무 영향이 없습니다.**

### 5️⃣ 화면에서 확인하고 커밋

`python run.py` 와 `npm run dev` 로 화면을 띄워 **예시 질문 3개가 각각 정상 동작하는지** 확인하세요.
답변과 하단의 실행 노드 배지가 함께 보이게 캡처해서 `teams/team3/screenshots/` 에 넣고,
`README.md` 3.1 에 붙인 뒤 커밋하시면 됩니다.

---

## 디버깅하는 두 가지 방법

### 1. 터미널에서 파일 하나만 실행하기

화면을 띄우지 않고 빠르게 확인할 때 씁니다.

```cmd
.venv\Scripts\python.exe teams\team3\workflow.py "테스트할 질문"
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
.venv\Scripts\python.exe run.py
```
```cmd
cd frontend
npm run dev
```

http://localhost:5173 에서 우리 조 탭을 열고 대화해봅니다.
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

`README.md` 는 템플릿이 이미 들어있습니다. 맨 위의 **주제 선정 회의** 표를 먼저 채우고, 세 장을 쓴 뒤,
맨 끝의 **산출물 정리 회의** 표까지 채우면 끝입니다. (두 회의 표 모두 일시 / 장소 / 참석자를 적습니다)

1. **LangGraph 워크플로우 설계** — State, 노드, 엣지, mermaid 다이어그램, 그렇게 설계한 이유
2. **프롬프트 엔지니어링** — 노드별 프롬프트 전문, 설계 의도, 개선 전/후
3. **실행 결과 & 회고** — 예시 질문 3개가 동작하는 화면 캡처, 잘 된 점과 한계, 배운 점

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

- [환경 구축 가이드](docs/SETUP_GUIDE.md) — 설치, `.env`, 기동(`python run.py` / `npm install`)
- [0조 예제 코드](teams/team0/workflow.py) — 4노드 + 조건분기 MultiAgent
- [0조 산출물 문서](teams/team0/README.md) — README 모범답안
