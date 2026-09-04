import subprocess
from pathlib import Path

from app.discovery import STATUS_NOT_IMPLEMENTED, STATUS_READY, discover_teams

ROOT = Path(__file__).resolve().parent.parent
TEAMS_DIR = ROOT / "teams"


def test_all_eight_team_folders_exist():
    entries = discover_teams(TEAMS_DIR)
    assert [e.number for e in entries] == [0, 1, 2, 3, 4, 5, 6, 7]


def test_team0_is_ready_and_others_are_not_implemented():
    entries = {e.number: e for e in discover_teams(TEAMS_DIR)}
    assert entries[0].status == STATUS_READY, entries[0].error
    for number in range(1, 8):
        assert entries[number].status == STATUS_NOT_IMPLEMENTED, entries[number].error


def test_template_folders_have_required_files():
    for number in range(1, 8):
        folder = TEAMS_DIR / f"team{number}"
        for name in ("__init__.py", "workflow.py", "prompts.py", "README.md"):
            assert (folder / name).exists(), f"{folder / name} 이 없습니다"


def test_no_internal_environment_wording_in_shared_files():
    """팀원에게 배포되는 파일에 특정 조직 환경을 암시하는 워딩이 없어야 합니다.

    검사 대상은 git 이 추적하는 파일뿐입니다. 리드 전용 문서와 이 검사 파일 자체는 제외합니다.
    """
    banned = ("사내", "보안망", "내부망")
    exempt = {"LEAD_GUIDE.md", Path(__file__).name}
    skip_dirs = {"superpowers"}

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()

    offenders = []
    for name in tracked:
        path = ROOT / name
        if path.suffix not in {".py", ".md", ".jsx", ".js", ".css", ".html"}:
            continue
        if path.name in exempt or set(path.parts) & skip_dirs:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        offenders += [f"{name}: {word}" for word in banned if word in text]
    assert not offenders, offenders
