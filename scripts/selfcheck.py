"""제출 전 자가 점검 스크립트입니다.

    python scripts/selfcheck.py team3     우리 조만 검사
    python scripts/selfcheck.py           전체 조를 한 번에 검사

계약을 지켰는지 확인해줍니다. 통과해야 화면에서 정상 동작합니다.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.discovery import STATUS_READY, discover_teams  # noqa: E402

REQUIRED_DOC_SECTIONS = (
    "## 1. LangGraph 워크플로우 설계",
    "## 2. 프롬프트 엔지니어링",
    "## 3. 실행 결과 & 회고",
)


def check(team_id: str) -> list[str]:
    """문제점 목록을 돌려줍니다. 비어 있으면 통과입니다."""
    problems: list[str] = []
    entry = next((e for e in discover_teams() if e.id == team_id), None)
    if entry is None:
        return [f"teams/{team_id} 폴더를 찾을 수 없습니다."]

    if entry.status != STATUS_READY:
        problems.append(f"그래프를 만들 수 없습니다: {entry.error}")

    info = getattr(entry.module, "TEAM_INFO", {}) or {}
    if not info.get("description"):
        problems.append("TEAM_INFO['description'] 이 비어 있습니다.")
    if len(info.get("examples") or []) < 3:
        problems.append("TEAM_INFO['examples'] 에 예시 질문을 3개 이상 넣어주세요.")

    readme = ROOT / "teams" / team_id / "README.md"
    if not readme.exists():
        problems.append("README.md 가 없습니다.")
    else:
        text = readme.read_text(encoding="utf-8")
        problems += [
            f"README.md 에 '{section}' 섹션이 없습니다."
            for section in REQUIRED_DOC_SECTIONS
            if section not in text
        ]
        if "```mermaid" not in text:
            problems.append("README.md 에 mermaid 워크플로우 다이어그램이 없습니다.")

    return problems


def report(team_id: str) -> bool:
    """한 조를 검사하고 결과를 출력합니다. 통과하면 True."""
    problems = check(team_id)
    if problems:
        print(f"[실패] {team_id} — {len(problems)}건을 고쳐주세요")
        for problem in problems:
            print(f"  - {problem}")
        return False

    print(f"[통과] {team_id} — 제출 준비가 되었습니다.")
    return True


def main() -> int:
    if len(sys.argv) > 2:
        print("사용법: python scripts/selfcheck.py [team3]")
        return 2

    # 인자를 주지 않으면 전체 조를 한 번에 검사합니다.
    if len(sys.argv) == 1:
        results = []
        for entry in discover_teams():
            results.append(report(entry.id))
            print()
        return 0 if all(results) else 1

    return 0 if report(sys.argv[1]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
