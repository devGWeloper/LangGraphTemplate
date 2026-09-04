# 환경 구축 가이드

파이썬을 처음 다루는 분도 그대로 따라 할 수 있게 적었습니다.
명령어는 복사해서 붙여넣으시면 됩니다. **한 단계씩 순서대로** 진행하세요.

> 🖥️ 이 문서의 모든 명령어는 **Windows 명령 프롬프트(cmd)** 기준입니다.
> 시작 메뉴에서 `cmd` 를 검색해 실행하시면 됩니다. PowerShell 말고 cmd 를 쓰세요.

---

## 0. 준비물

| 프로그램 | 버전 | 확인 방법 |
|---|---|---|
| Python | 3.11 이상 | `python --version` |
| Node.js | 18 이상 | `node --version` |
| Git | 아무거나 | `git --version` |

### Python 설치

명령 프롬프트에 `python --version` 을 쳤을 때 `Python 3.11.x` 처럼 나오면 넘어가세요.

안 나온다면 [python.org/downloads](https://www.python.org/downloads/) 에서 3.11 이상을 받아 설치합니다.

> ⚠️ **설치할 때 꼭 확인하세요**: 설치 첫 화면 맨 아래 **"Add python.exe to PATH"** 체크박스를
> 반드시 켜야 합니다. 이걸 안 켜면 명령 프롬프트에서 `python` 명령을 찾지 못합니다.
> 이미 설치했다면 설치 파일을 다시 실행해 "Modify" 로 고칠 수 있습니다.
>
> 설치 후에는 **명령 프롬프트를 닫았다가 다시 열어야** 인식됩니다.

### Node.js 설치

화면(프론트엔드)을 빌드할 때만 필요합니다.
[nodejs.org](https://nodejs.org/) 에서 LTS 버전을 받아 설치하세요.
설치 후 역시 명령 프롬프트를 다시 열어주세요.

---

## 1. 저장소 받기

작업할 폴더로 이동한 뒤 클론합니다.

```cmd
cd C:\work
git clone <저장소 주소>
cd LangGraphTemplate
```

그리고 **우리 조 브랜치**로 이동합니다. (3조라면)

```cmd
git checkout team3
```

> 브랜치 이름은 리드가 안내해드립니다. `git branch -r` 로 목록을 볼 수 있습니다.

---

## 2. 가상환경 만들기

가상환경은 이 프로젝트에서 쓸 파이썬 패키지를 **이 폴더 안에만** 설치하는 공간입니다.
컴퓨터 전체 파이썬을 더럽히지 않으려고 씁니다.

```cmd
python -m venv .venv
.venv\Scripts\activate
```

성공하면 명령 프롬프트 앞에 **`(.venv)`** 가 붙습니다.

```
(.venv) C:\...\LangGraphTemplate>
```

이게 보여야 다음 단계로 갑니다.

> 💡 명령 프롬프트를 새로 열 때마다 `.venv\Scripts\activate` 를 다시 실행해야 합니다.
> 매번 치기 귀찮으면 활성화 없이 이렇게 해도 됩니다.
>
> ```cmd
> .venv\Scripts\python.exe run.py
> ```

---

## 3. 패키지 설치

```cmd
pip install -r requirements.txt
```

2~3분 걸립니다. 마지막에 `Successfully installed ...` 가 나오면 성공입니다.

---

## 4. 접속 정보 설정 (.env)

`.env.example` 을 복사해서 `.env` 파일을 만듭니다.

```cmd
copy .env.example .env
```

그리고 `.env` 를 메모장이나 편집기로 열어 값을 채웁니다.

```cmd
notepad .env
```

```
LLM_BASE_URL=여기에_엔드포인트_주소
LLM_API_KEY=여기에_키
LLM_MODEL=여기에_모델_이름
PORT=8021
```

> 🔒 `.env` 는 `.gitignore` 에 등록되어 있어 커밋되지 않습니다. **키를 코드에 직접 적지 마세요.**
> 값은 리드에게 받으시면 됩니다.

---

## 5. 화면 빌드

```cmd
cd frontend
npm install
npm run build
cd ..
```

`npm install` 은 처음 한 번만 하면 됩니다.
`frontend/dist` 폴더가 생기면 성공입니다.

---

## 6. 서버 실행

```cmd
python run.py
```

명령 프롬프트에 이렇게 나옵니다.

```
Uvicorn running on http://0.0.0.0:8021
```

브라우저에서 **http://localhost:8021** 로 접속하세요.
탭이 8개(0조 ~ 7조) 보이면 성공입니다.

- **0조 탭**: 여행지 추천 예제가 바로 동작합니다. 먼저 여기서 대화해보세요.
- **우리 조 탭**: 아직 "개발 중" 상태입니다. 이제 `teams/teamN/workflow.py` 를 채우면 됩니다.

서버를 끄려면 명령 프롬프트에서 `Ctrl + C` 를 누릅니다.

> 💡 `run.py` 는 자동 리로드가 켜져 있어서, 코드를 저장하면 서버가 알아서 다시 뜹니다.
> 화면은 브라우저 새로고침(F5)만 하면 됩니다.

---

## 7. (선택) 화면을 따로 띄우고 개발하기

화면 코드는 수정할 일이 없지만, 응답 속도가 빠른 개발 서버로 쓰고 싶다면
명령 프롬프트 **두 개**를 띄웁니다.

첫 번째 창 (백엔드):

```cmd
python run.py
```

두 번째 창 (프론트엔드):

```cmd
cd frontend
npm run dev
```

그리고 http://localhost:5173 으로 접속합니다. `/api` 요청은 자동으로 8021 로 전달됩니다.

---

## 8. 화면 없이 빠르게 돌려보기

개발 중에는 서버를 켜고 브라우저를 오가는 것보다, 파일 하나만 실행해보는 게 빠릅니다.

```cmd
python teams\team3\workflow.py "테스트할 질문"
```

노드가 하나씩 실행되면서 각 노드가 만든 값이 출력됩니다.
어느 노드에서 이상해지는지 바로 보입니다.

---

## 9. 제출 전 자가 점검

```cmd
python scripts\selfcheck.py team3
```

`[통과] 제출 준비가 되었습니다.` 가 나오면 커밋하시면 됩니다.

전체 조를 한 번에 보려면 조 이름 없이 실행하세요.

```cmd
python scripts\selfcheck.py
```

---

## 자주 겪는 오류

### `'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램... 이 아닙니다`

파이썬이 PATH에 없습니다. 설치할 때 "Add python.exe to PATH" 를 체크하지 않은 경우입니다.
설치 파일을 다시 실행해 "Modify" → PATH 추가를 켜고, **명령 프롬프트를 닫았다가 다시 여세요.**
그래도 안 되면 `py` 명령으로 대체해보세요. (`py -m venv .venv` 처럼)

### `ModuleNotFoundError: No module named 'fastapi'`

가상환경이 활성화되지 않았습니다. 명령 프롬프트 앞에 `(.venv)` 가 있는지 확인하세요.
없으면 `.venv\Scriptsctivate` 를 다시 실행합니다.

### `ModuleNotFoundError: No module named 'app'`

프로젝트 최상위 폴더에서 실행하지 않았습니다.
`cd` 로 `LangGraphTemplate` 폴더까지 이동한 뒤 실행하세요.
지금 어디인지는 `cd` 만 쳐보면 나옵니다.

### `[Errno 10048] error while attempting to bind on address ... 8021`

8021 포트를 이미 다른 프로그램이 쓰고 있습니다.
이전에 켜둔 서버가 있다면 그 터미널에서 `Ctrl + C` 로 끄거나, `.env` 의 `PORT` 를 8022 등으로 바꾸세요.

### 화면에 `.env 파일에 다음 값이 비어 있습니다` 가 뜸

4번 단계의 `.env` 설정이 안 되어 있습니다. 값을 채운 뒤 서버를 다시 실행하세요.

### `npm: command not found`

Node.js 가 설치되지 않았습니다. [nodejs.org](https://nodejs.org/) 에서 LTS 를 설치하고
터미널을 **완전히 닫았다가 다시 열어** 주세요.

### 화면은 뜨는데 탭이 하나도 없음

백엔드가 안 떠 있는 상태에서 `frontend/dist` 만 열었을 가능성이 큽니다.
`python run.py` 로 서버를 켠 뒤 http://localhost:8021 로 접속하세요.
