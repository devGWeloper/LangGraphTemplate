# 환경 구축 가이드

Windows 기준입니다. **설치 → `.env` 채우기 → 기동** 세 단계면 끝납니다.
막히면 화면을 캡처해서 리드에게 보내주세요.

**미리 깔려 있어야 하는 것**

- Python 3.11 이상 — [python.org/downloads](https://www.python.org/downloads/)
  (설치 첫 화면의 **"Add python.exe to PATH"** 체크 필수)
- Node.js LTS — [nodejs.org](https://nodejs.org/)

설치했는데 인식이 안 되면 창을 닫았다가 다시 여세요.

---

## 1단계 — 설치

프로젝트 폴더의 **`setup.bat`** 을 더블클릭하세요. 3~5분 걸립니다.
파이썬 패키지 설치, `.env` 생성, 화면 빌드까지 한 번에 됩니다.

직접 하고 싶다면 cmd 에서 프로젝트 폴더로 이동한 뒤:

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
cd frontend
npm install
npm run build
cd ..
```

---

## 2단계 — `.env` 채우기

`.env` 는 **프로젝트 최상위 폴더**(`run.py` 와 같은 자리)에 있습니다.
아래 값을 리드에게 받아 채우고 저장하세요.

```
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
PORT=8021
```

> ⚠️ 메모장 "새로 만들기 → 저장"으로 만들면 `.env.txt` 가 됩니다. 꼭 `copy .env.example .env` 를 쓰세요.

---

## 3단계 — 기동

**`start.bat`** 을 더블클릭하면 서버가 뜨고 잠시 후 브라우저가 열립니다.

cmd 에서 직접 띄우려면 — **프로젝트 최상위 폴더에서** 실행해야 합니다:

```cmd
.venv\Scripts\python.exe run.py
```

```
  주소 : http://localhost:8021
  서버를 끄려면 Ctrl + C
```

브라우저가 안 열리면 **http://localhost:8021** 로 직접 들어가세요.
탭이 8개(0조 ~ 7조) 보이면 성공입니다.

**화면(프론트엔드)을 다시 빌드해야 할 때** — 처음 받았거나 `frontend/` 가 바뀌었을 때만:

```cmd
cd frontend
npm install
npm run build
cd ..
```

`npm install` 은 처음 한 번이면 되고, 이후에는 `npm run build` 만 다시 돌리면 됩니다.
빌드 결과는 `frontend\dist` 에 들어가고 서버가 그걸 그대로 서빙합니다.

> 💡 파이썬 코드를 고치고 저장하면 서버가 알아서 다시 뜹니다. 브라우저는 F5 만 누르세요.

---

## 개발할 때 — 화면 없이 빠르게 돌려보기

서버를 켜고 브라우저를 오가는 것보다 파일 하나만 실행하는 게 빠릅니다.

```cmd
.venv\Scripts\python.exe teams\team3\workflow.py "테스트할 질문"
```

노드가 하나씩 실행되면서 각 노드가 만든 값이 출력됩니다.

---

## 잘 안 될 때

| 증상 | 확인할 것 |
|---|---|
| `setup.bat` 창이 깜빡하고 사라짐 | 폴더를 `C:\work\LangGraphTemplate` 처럼 짧고 한글·공백 없는 경로로 옮기기 |
| 파이썬 / Node.js 를 못 찾음 | 설치 여부와 PATH 체크, 설치 후 창 다시 열기 |
| "LLM 접속 정보가 설정되지 않았습니다" | `.env` 값 세 개 확인 후 **서버 재시작** (`dir .env*` 로 `.env.txt` 인지도 확인) |
| `ModuleNotFoundError: No module named 'app'` | 프로젝트 최상위 폴더에서 실행했는지 확인 |
| 포트 8021 사용 중 | 이전 서버 창에서 `Ctrl + C`, 또는 `.env` 의 `PORT` 를 8022 로 변경 |

그래도 안 되면 오류 메시지를 그대로 캡처해서 리드에게 보내주세요.
