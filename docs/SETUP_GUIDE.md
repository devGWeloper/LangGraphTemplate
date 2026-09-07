# 환경 구축 가이드

Windows 기준입니다. **저장소 받기 → 설치 → `.env` 채우기 → 기동** 순서로 진행합니다.
막히면 화면을 캡처해서 리드에게 보내주세요.

**미리 깔려 있어야 하는 것**

- Python 3.11 이상 — [python.org/downloads](https://www.python.org/downloads/)
  (설치 첫 화면의 **"Add python.exe to PATH"** 체크 필수)
- Node.js LTS — [nodejs.org](https://nodejs.org/)

설치했는데 인식이 안 되면 창을 닫았다가 다시 여세요.

---

## 0단계 — 저장소 받고 우리 조 브랜치로 이동

Git 이 없으면 [git-scm.com](https://git-scm.com/download/win) 에서 받아 설치하세요. (설정은 전부 기본값)

cmd 를 열고, 프로젝트를 받아둘 폴더(예: `C:\work`, 없으면 미리 만들어 두세요)에서 아래를 실행합니다.
**`team3` 은 자기 조 번호로 바꾸세요.**

```cmd
cd C:\work
git clone <저장소 주소>
cd LangGraphTemplate
git checkout team3
```

`cd` 뒤의 폴더 이름은 클론하면 생기는 저장소 이름입니다.

제대로 이동했는지 확인합니다.

```cmd
git branch --show-current
```

`team3` 이 나오면 정상입니다. `main` 이 나오면 `git checkout team3` 을 다시 실행하세요.

> ⚠️ **브랜치 이동을 건너뛰고 `main` 에서 작업하면 안 됩니다.** 나중에 제출할 곳이 없습니다.
> 조 브랜치는 리드가 미리 만들어 뒀으므로 `git checkout team3` 만 하면 바로 붙습니다.

작업이 끝나면 우리 조 브랜치에 그대로 올립니다.

```cmd
git add teams/team3
git commit -m "3조 산출물"
git push origin team3
```

---

## 1단계 — 설치

**cmd** 를 열고 프로젝트 폴더로 이동한 뒤, 아래를 위에서부터 순서대로 실행하세요.
처음 한 번만 하면 됩니다. 3~5분 걸립니다.

```cmd
cd C:\work\LangGraphTemplate

python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env

cd frontend
npm install
cd ..
```

| 명령 | 하는 일 |
|---|---|
| `python -m venv .venv` | 이 프로젝트 전용 파이썬 환경을 만듭니다 |
| `pip install -r requirements.txt` | LangGraph·FastAPI 등 파이썬 패키지 설치 (2~3분) |
| `copy .env.example .env` | 접속 정보 파일을 만듭니다 |
| `npm install` | 화면(React) 패키지 설치 (1~2분) |

> `.venv\Scripts\python.exe` 를 쓰면 activate 없이 이 프로젝트 환경의 파이썬이 실행됩니다.

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

**cmd 창을 두 개** 열고 하나씩 실행합니다. 둘 다 켜져 있어야 합니다.

**창 1 — 백엔드** (프로젝트 최상위 폴더에서)

```cmd
.venv\Scripts\python.exe run.py
```

```
  http://localhost:8021 에서 대기 중
  끄려면 Ctrl + C
```

**창 2 — 화면**

```cmd
cd frontend
npm run dev
```

```
  VITE ready
  Local: http://localhost:5173
```

브라우저에서 **http://localhost:5173** 을 여세요. 탭이 8개(0조 ~ 7조) 보이면 성공입니다.
화면(5173)이 `/api` 요청을 백엔드(8021)로 넘기는 구조라, 접속은 **5173** 으로 합니다.

> `npm install` 은 1단계에서 한 번만 하면 됩니다. 이후에는 `npm run dev` 만 쓰면 됩니다.
> 파이썬 코드를 고치고 저장하면 백엔드가 알아서 다시 뜨고, 화면 코드는 저장하는 순간 반영됩니다.

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
| `git clone` 이 인증을 요구함 | Bitbucket 계정으로 로그인하면 됩니다. 계속 실패하면 리드에게 접근 권한을 요청하세요 |
| `git push` 가 거부됨 (`main`) | `git branch --show-current` 로 우리 조 브랜치인지 확인. `main` 이면 `git checkout team3` 후 다시 커밋 |
| `python -m venv .venv` 가 실패함 | 폴더를 `C:\work\LangGraphTemplate` 처럼 짧고 한글·공백 없는 경로로 옮기기 (OneDrive 동기화 폴더 주의) |
| 파이썬 / Node.js 를 못 찾음 | 설치 여부와 PATH 체크, 설치 후 창 다시 열기 |
| "LLM 접속 정보가 설정되지 않았습니다" | `.env` 값 세 개 확인 후 **서버 재시작** (`dir .env*` 로 `.env.txt` 인지도 확인) |
| `ModuleNotFoundError: No module named 'app'` | 프로젝트 최상위 폴더에서 실행했는지 확인 |
| 포트 8021 / 5173 이 사용 중 | 이전에 켜둔 cmd 창에서 `Ctrl + C` 로 끄기 |

그래도 안 되면 오류 메시지를 그대로 캡처해서 리드에게 보내주세요.
