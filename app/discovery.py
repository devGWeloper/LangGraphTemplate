"""teams/ 폴더를 스캔해 조별 워크플로우 모듈을 찾아옵니다.

이 파일은 수정하지 마세요. 조원은 자기 폴더의 workflow.py 만 작성하면
서버가 알아서 탭을 만들어 줍니다.
"""
from __future__ import annotations

import importlib.util
import re
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

STATUS_READY = "ready"
STATUS_NOT_IMPLEMENTED = "not_implemented"
STATUS_ERROR = "error"

TEAMS_DIR = Path(__file__).resolve().parent.parent / "teams"
_FOLDER_PATTERN = re.compile(r"^team(\d+)$")


@dataclass
class TeamEntry:
    id: str
    number: int
    name: str
    description: str = ""
    examples: list[str] = field(default_factory=list)
    status: str = STATUS_NOT_IMPLEMENTED
    error: str | None = None
    module: ModuleType | None = None
    _graph: object | None = field(default=None, repr=False)


def _load_module(folder: Path) -> ModuleType:
    """teams/teamN/workflow.py 를 독립 모듈로 import 합니다."""
    workflow = folder / "workflow.py"
    spec = importlib.util.spec_from_file_location(f"teams.{folder.name}.workflow", workflow)
    if spec is None or spec.loader is None:
        raise ImportError(f"{workflow} 를 불러올 수 없습니다")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_entry(folder: Path, number: int) -> TeamEntry:
    entry = TeamEntry(id=folder.name, number=number, name=f"{number}조")

    if not (folder / "workflow.py").exists():
        entry.error = "workflow.py 파일이 없습니다."
        return entry

    try:
        entry.module = _load_module(folder)
    except Exception:
        entry.status = STATUS_ERROR
        entry.error = traceback.format_exc(limit=3)
        return entry

    info = getattr(entry.module, "TEAM_INFO", None)
    if isinstance(info, dict):
        entry.name = info.get("name") or entry.name
        entry.description = info.get("description") or ""
        entry.examples = list(info.get("examples") or [])

    builder = getattr(entry.module, "build_graph", None)
    if not callable(builder):
        entry.error = "workflow.py 에 build_graph() 함수가 없습니다."
        return entry

    try:
        entry._graph = builder()
    except NotImplementedError as exc:
        entry.error = str(exc) or "아직 구현되지 않았습니다."
        return entry
    except Exception:
        entry.status = STATUS_ERROR
        entry.error = traceback.format_exc(limit=3)
        return entry

    entry.status = STATUS_READY
    return entry


def discover_teams(teams_dir: Path | None = None) -> list[TeamEntry]:
    """조 폴더를 번호 오름차순으로 스캔해 목록을 돌려줍니다."""
    root = Path(teams_dir) if teams_dir else TEAMS_DIR
    entries: list[TeamEntry] = []
    if not root.exists():
        return entries

    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        matched = _FOLDER_PATTERN.match(folder.name)
        if not matched:
            continue
        entries.append(_build_entry(folder, int(matched.group(1))))

    entries.sort(key=lambda e: e.number)
    return entries


def get_graph(entry: TeamEntry) -> object:
    """디스커버리 때 만들어 둔 그래프를 돌려줍니다."""
    if entry.status != STATUS_READY or entry._graph is None:
        raise RuntimeError(entry.error or f"{entry.name} 은 아직 실행할 수 없습니다.")
    return entry._graph
