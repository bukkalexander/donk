from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, Dict, Iterable, List, Tuple

import pytest

from .context import (
    DATA_DIR_PATH,
    SIMPLE_DATASET_PATH,
    WORKSPACE_ROOT_PATH,
)


@dataclass(frozen=True)
class ProjectLayout:
    name: str
    run_root: Path
    project_root: Path
    expected_root: Path
    actual_root: Path


@pytest.fixture(scope="session")
def repo_workspace_root() -> Path:
    WORKSPACE_ROOT_PATH.mkdir(parents=True, exist_ok=True)
    return WORKSPACE_ROOT_PATH


@pytest.fixture
def project_workspace(repo_workspace_root: Path, request: pytest.FixtureRequest) -> Path:
    safe_nodeid = request.node.nodeid.replace("/", "__").replace("::", "__")
    base = repo_workspace_root / safe_nodeid
    base.mkdir(parents=True, exist_ok=True)

    index = 1
    while True:
        candidate = base / f"run_{index:03d}"
        if not candidate.exists():
            candidate.mkdir()
            return candidate
        index += 1


@pytest.fixture
def project_factory(project_workspace: Path) -> Callable[[Path], ProjectLayout]:
    def _build(dataset_path: Path) -> ProjectLayout:
        dataset_name = dataset_path.name
        expected_root = project_workspace / "expected" / dataset_name
        actual_root = project_workspace / "actual" / dataset_name

        shutil.copytree(dataset_path / "out", expected_root, dirs_exist_ok=True)
        shutil.copytree(dataset_path / "in", actual_root, dirs_exist_ok=True)
        return ProjectLayout(
            name=dataset_name,
            run_root=project_workspace,
            project_root=actual_root,  # compiler entry-point
            expected_root=expected_root,
            actual_root=actual_root,
        )
    return _build


def _walk_files(root: Path) -> Dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _diff_text(expected: Path, actual: Path) -> str | None:
    try:
        expected_text = expected.read_text()
        actual_text = actual.read_text()
    except UnicodeDecodeError:
        return None

    if expected_text == actual_text:
        return None

    diff_lines = difflib.unified_diff(
        expected_text.splitlines(),
        actual_text.splitlines(),
        fromfile=str(expected),
        tofile=str(actual),
        n=3,
    )
    return "\n".join(diff_lines)


def compare_trees(expected_root: Path, actual_root: Path) -> List[str]:
    differences: List[str] = []
    expected_files = _walk_files(expected_root)
    actual_files = _walk_files(actual_root)

    missing = sorted(expected_files.keys() - actual_files.keys())
    if missing:
        differences.append(f"Missing files in actual output: {missing}")

    unexpected = sorted(actual_files.keys() - expected_files.keys())
    if unexpected:
        differences.append(f"Unexpected files produced: {unexpected}")

    shared = expected_files.keys() & actual_files.keys()
    for rel_path in sorted(shared):
        expected_file = expected_files[rel_path]
        actual_file = actual_files[rel_path]

        text_diff = _diff_text(expected_file, actual_file)
        if text_diff is None:
            if expected_file.read_bytes() != actual_file.read_bytes():
                differences.append(f"Binary content mismatch at {rel_path}")
        elif text_diff:
            differences.append(f"Text content mismatch at {rel_path}:\n{text_diff}")

    return differences


def test_simple_compilation(project_factory: Callable[[Path], ProjectLayout]) -> None:
    layout = project_factory(SIMPLE_DATASET_PATH)

    compiler = pytest.importorskip("donk.compiler")
    compiler.compile_project(
        project_root=layout.project_root,
        output_dir=layout.actual_root,
    )  # TODO: replace with real invocation of the donk compiler.

    diffs = compare_trees(layout.expected_root, layout.actual_root)
    assert not diffs, "Output mismatch detected:\n" + "\n".join(diffs)
