import textwrap
from pathlib import Path

import pytest

from app.discovery import (
    STATUS_ERROR,
    STATUS_NOT_IMPLEMENTED,
    STATUS_READY,
    discover_teams,
    get_graph,
)

READY_BODY = '''
TEAM_INFO = {"name": "테스트 조", "description": "설명", "examples": ["예시"]}

def build_graph():
    class FakeGraph:
        pass
    return FakeGraph()
'''


def _make_team(root: Path, number: int, body: str) -> None:
    folder = root / f"team{number}"
    folder.mkdir(parents=True)
    (folder / "__init__.py").write_text("", encoding="utf-8")
    (folder / "workflow.py").write_text(textwrap.dedent(body), encoding="utf-8")


def test_discovers_teams_sorted_by_number(tmp_path):
    _make_team(tmp_path, 3, READY_BODY)
    _make_team(tmp_path, 0, READY_BODY)
    entries = discover_teams(tmp_path)
    assert [e.number for e in entries] == [0, 3]
    assert [e.id for e in entries] == ["team0", "team3"]


def test_ready_team_exposes_team_info(tmp_path):
    _make_team(tmp_path, 1, READY_BODY)
    entry = discover_teams(tmp_path)[0]
    assert entry.status == STATUS_READY
    assert entry.name == "테스트 조"
    assert entry.examples == ["예시"]
    assert entry.error is None


def test_missing_build_graph_is_not_implemented(tmp_path):
    _make_team(tmp_path, 2, "TEAM_INFO = {'name': '2조'}\n")
    entry = discover_teams(tmp_path)[0]
    assert entry.status == STATUS_NOT_IMPLEMENTED


def test_not_implemented_error_is_not_implemented(tmp_path):
    _make_team(tmp_path, 4, '''
def build_graph():
    raise NotImplementedError("아직 구현하지 않았습니다")
''')
    entry = discover_teams(tmp_path)[0]
    assert entry.status == STATUS_NOT_IMPLEMENTED
    assert "아직 구현하지" in entry.error


def test_import_error_is_isolated(tmp_path):
    _make_team(tmp_path, 5, "import definitely_not_a_real_module\n")
    _make_team(tmp_path, 6, READY_BODY)
    entries = {e.number: e for e in discover_teams(tmp_path)}
    assert entries[5].status == STATUS_ERROR
    assert "definitely_not_a_real_module" in entries[5].error
    assert entries[6].status == STATUS_READY


def test_missing_team_info_falls_back_to_folder_name(tmp_path):
    _make_team(tmp_path, 7, '''
def build_graph():
    return object()
''')
    assert discover_teams(tmp_path)[0].name == "7조"


def test_non_team_folders_are_ignored(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "notes").mkdir()
    _make_team(tmp_path, 0, READY_BODY)
    assert len(discover_teams(tmp_path)) == 1


def test_missing_workflow_file_is_not_implemented(tmp_path):
    (tmp_path / "team1").mkdir()
    entry = discover_teams(tmp_path)[0]
    assert entry.status == STATUS_NOT_IMPLEMENTED
    assert "workflow.py" in entry.error


def test_get_graph_builds_only_once(tmp_path):
    _make_team(tmp_path, 0, '''
calls = []

def build_graph():
    calls.append(1)
    return object()
''')
    entry = discover_teams(tmp_path)[0]
    assert get_graph(entry) is get_graph(entry)
    assert len(entry.module.calls) == 1


def test_get_graph_raises_for_non_ready_entry(tmp_path):
    _make_team(tmp_path, 0, "TEAM_INFO = {'name': '0조'}\n")
    with pytest.raises(RuntimeError):
        get_graph(discover_teams(tmp_path)[0])
