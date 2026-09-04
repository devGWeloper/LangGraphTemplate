# 리드 운영 가이드 (대외 비공개)

> 이 문서는 리드(운영자) 전용입니다. 팀원에게 배포하는 다른 문서(`README.md`, `docs/*`)와
> 모든 소스코드에는 사내 환경을 암시하는 워딩이 하나도 들어 있지 않습니다.
> 이 `LEAD_GUIDE.md` 만 예외입니다. 조원 제출물이 합쳐진 뒤 다시 한 번 확인하려면:
>
> ```bash
> git ls-files | grep -E '\.(py|md|jsx|js|css|html)$' | grep -v LEAD_GUIDE.md | xargs grep -n "사내\|보안망\|내부망"
> ```
>
> 아무것도 안 나오면 정상입니다. 이 파일 자체를 저장소에서 빼고 싶다면
> `git rm --cached LEAD_GUIDE.md` 후 `.gitignore` 에 추가하시면 됩니다.

---

## 1. 저장소 준비

사내 Bitbucket에 저장소를 하나 만들고 main을 올립니다.

```bash
git remote set-url origin <사내 Bitbucket 저장소 주소>
git push -u origin main
```

조별 브랜치를 main에서 분기해 각 조에 배정합니다.

```bash
for i in 1 2 3 4 5 6 7; do
  git branch team$i main
  git push origin team$i
done
```

> Windows PowerShell이라면:
> ```powershell
> 1..7 | ForEach-Object { git branch "team$_" main; git push origin "team$_" }
> ```

각 조에는 자기 브랜치의 push 권한만 주면 실수로 main을 건드리는 일이 없습니다.

---

## 2. 조별 공지 문구 (그대로 복사해 쓰세요)

> **AI 챌린지 안내**
>
> 저장소: `<주소>` / 여러분 조 브랜치: `team3`
>
> 1. 저장소를 클론하고 `git checkout team3` 으로 브랜치를 옮깁니다.
> 2. `docs/SETUP_GUIDE.md` 를 따라 환경을 만듭니다. (파이썬 설치부터 단계별로 있습니다)
> 3. `python run.py` 로 서버를 켜고 http://localhost:8021 에 접속합니다.
> 4. **0조 탭에서 여행지 추천 예제와 먼저 대화해보고**, `teams/team0/` 코드를 읽어보세요.
> 5. `teams/team3/` 폴더 안의 `workflow.py`, `prompts.py`, `README.md` 세 개만 채우면 됩니다.
> 6. 제출 전에 `python scripts/selfcheck.py team3` 을 돌려 `[통과]` 를 확인하세요.
>
> **주의: `teams/team3/` 폴더 밖의 파일은 절대 수정하지 마세요.** 나중에 합칠 때 충돌이 납니다.
>
> 마감: `<날짜>` / 제출: 자기 브랜치에 push

`.env` 값(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)은 저장소에 넣지 말고 별도 채널로 전달하세요.

---

## 3. 조원이 지켜야 할 규칙 (충돌 방지의 전부)

| 규칙 | 이유 |
|---|---|
| `teams/teamN/` 폴더 안에서만 작업 | 조별로 파일이 완전히 분리되어 merge 충돌이 구조적으로 발생하지 않음 |
| `requirements.txt` 는 맨 아래 `# --- 조별 추가 ---` 구역에만 append | 유일하게 공유되는 파일. 맨 아래에만 추가하면 충돌이 나도 "양쪽 다 살리기"로 끝남 |
| `.env` 커밋 금지 | `.gitignore` 에 이미 등록되어 있음 |
| `app/`, `frontend/`, `docs/` 수정 금지 | 공용 코드 |

탭 등록은 자동입니다. 조원이 등록 파일을 고칠 일이 없으므로 그쪽 충돌은 애초에 발생하지 않습니다.

---

## 4. 취합 절차

```bash
git checkout main
git pull

git merge team1
git merge team2
git merge team3
git merge team4
git merge team5
git merge team6
git merge team7
```

**충돌이 날 수 있는 파일은 `requirements.txt` 하나뿐입니다.**
조별 추가 구역에서 나는 충돌이므로 해결은 항상 "양쪽 다 살리기"입니다.

```
<<<<<<< HEAD
beautifulsoup4==4.12.3
=======
tavily-python==0.5.0
>>>>>>> team4
```
→ 두 줄 다 남기고 충돌 마커만 지우면 됩니다.

만약 조 폴더 밖 파일에서 충돌이 났다면 그 조가 규칙을 어긴 것입니다.
`git log --stat team3 ^main` 으로 어떤 파일을 건드렸는지 확인하고 되돌리세요.

각 조가 규칙을 지켰는지 미리 확인하려면:

```bash
git diff --name-only main..team3 | grep -v '^teams/team3/'
```

아무것도 안 나오면 정상입니다.

---

## 5. 취합 후 검증

```bash
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
python scripts/selfcheck.py          # 전체 조 계약·문서 요건 일괄 검사
python run.py
```

http://localhost:8021 에 접속해 확인할 것:

- [ ] 탭이 8개(0조~7조) 보이는가
- [ ] 각 조 램프가 켜져 있는가 (앰버 = 정상, 빈 원 = 미구현, 빨강 = 오류)
- [ ] 0조 여행지 추천이 동작하는가
- [ ] 각 조 탭에서 예시 질문으로 실제 대화가 되는가
- [ ] 답변 아래 실행 노드 경로가 표시되는가

한 조에 오류가 있어도 서버는 죽지 않고 그 탭만 빨간 램프 + 오류 메시지가 뜹니다.
시연 전에 문제 있는 조를 미리 잡아낼 수 있습니다.

특정 조만 화면 없이 터미널에서 돌려보려면:

```bash
python teams/team3/workflow.py "테스트할 질문"
```

노드가 하나씩 실행되면서 각 노드가 만든 값이 출력됩니다. 어느 노드에서 이상해지는지 바로 보입니다.

---

## 6. 평가

Bitbucket에서 `teams/teamN/README.md` 를 열면 세 장이 순서대로 나옵니다. 스크롤만 내리면서 채점하세요.
mermaid 다이어그램은 Bitbucket에서 그대로 렌더링됩니다.

| 항목 | 배점 | 확인 지점 |
|---|---|---|
| **LangGraph 워크플로우 설계** | 40 | 1.1~1.3 표가 채워졌는가 / 1.4 다이어그램이 실제 코드와 일치하는가 / **1.5 "왜 노드를 나눴는가"에 납득할 이유가 있는가** |
| **프롬프트 엔지니어링** | 35 | 2장에 노드별 프롬프트 전문이 있는가 / **개선 전→후가 구체적인가 (실제로 뭐가 잘못 나왔는지 예시가 있는가)** |
| **실행 결과 & 회고** | 25 | 3.1에 실행 예시 2건, 그중 **실패·엣지 케이스가 포함**되었는가 / 한계를 솔직하게 적었는가 |

굵게 표시한 항목이 변별력이 갈리는 지점입니다.
표만 채우고 "왜"가 없는 문서와, 실패 사례를 정직하게 남긴 문서의 차이를 보시면 됩니다.

**감점 사유**
- 다이어그램과 실제 코드가 다름 (설계 항목에서 감점)
- 프롬프트 개선 기록이 "더 구체적으로 썼다" 수준으로 추상적임
- 실행 예시가 성공 케이스만 있음
- `teams/teamN/` 밖의 파일을 수정함

**참고 자료**
- `teams/team0/README.md` — 세 장을 모두 채운 모범답안. 채점 기준선으로 쓰세요.
- `scripts/selfcheck.py` — 형식 요건(섹션 3개, mermaid, TEAM_INFO)은 이 스크립트가 기계적으로 잡아줍니다.
  통과 못 한 제출물은 형식 미비로 먼저 걸러낼 수 있습니다.

---

## 7. 메모

- **주제·기획 정의 항목은 조별 README에서 뺐습니다.** 조별로 어떤 주제를 잡았는지는
  리드가 0조 문서나 별도 표에서 관리하기로 한 결정입니다. 조원 문서는 설계·프롬프트·회고 세 장에 집중합니다.
- 조 폴더는 `team0` ~ `team7` 고정입니다. 조가 늘어나면 `teams/team8/` 폴더를 만들고
  `workflow.py`, `prompts.py`, `README.md` 를 넣기만 하면 탭이 자동으로 하나 더 생깁니다.
  등록 코드를 고칠 필요가 없습니다.
- 탭 이름은 조원이 `TEAM_INFO["name"]` 에 쓴 값이 그대로 나옵니다. 시연 전에 한 번 훑어보세요.
- 포트를 바꾸려면 `.env` 의 `PORT` 값을 고치면 됩니다.
