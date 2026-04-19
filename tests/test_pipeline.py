"""Tests for RenderPipeline — happy path and profile switching."""

from __future__ import annotations

from pathlib import Path

import pytest

from sumd.pipeline import RenderPipeline


@pytest.fixture
def proj_dir(tmp_path: Path) -> Path:
    """Minimal project directory with just pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "testpkg"\nversion = "1.2.3"\ndescription = "Test package"\n',
        encoding="utf-8",
    )
    return tmp_path


def test_pipeline_run_returns_string(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert isinstance(content, str)
    assert len(content) > 0


def test_pipeline_output_has_h1(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="rich")
    lines = content.splitlines()
    h1_lines = [line for line in lines if line.startswith("# ") and not line.startswith("## ")]
    assert h1_lines, "output must have an H1 title"


def test_pipeline_output_has_metadata(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert "## Metadata" in content
    assert "testpkg" in content
    assert "1.2.3" in content


def test_pipeline_return_sources(proj_dir: Path) -> None:
    result = RenderPipeline(proj_dir).run(profile="rich", return_sources=True)
    assert isinstance(result, tuple)
    content, sources = result
    assert isinstance(content, str)
    assert isinstance(sources, list)


def test_pipeline_profile_minimal(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="minimal")
    assert "## Metadata" in content
    # Sections excluded from minimal
    assert "## Interfaces" not in content
    assert "## Code Analysis" not in content


def test_pipeline_profile_refactor(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="refactor")
    assert "## Metadata" in content
    assert "## Architecture" in content
    # Refactor profile excludes these
    assert "## Interfaces" not in content
    assert "## Workflows" not in content


def test_pipeline_with_modules(proj_dir: Path) -> None:
    """Pipeline picks up python modules in pkg dir."""
    pkg = proj_dir / "testpkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "core.py").write_text("def run(): pass\n")
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert "testpkg" in content


def test_pipeline_with_taskfile(proj_dir: Path) -> None:
    (proj_dir / "Taskfile.yml").write_text(
        'version: "3"\ntasks:\n  test:\n    desc: Run tests\n    cmds:\n      - pytest\n',
        encoding="utf-8",
    )
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert "## Workflows" in content
    assert "test" in content


def test_pipeline_with_dependencies(proj_dir: Path) -> None:
    (proj_dir / "pyproject.toml").write_text(
        '[project]\nname = "testpkg"\nversion = "0.1.0"\ndescription = "x"\n'
        'dependencies = ["click>=8.0", "pyyaml>=6.0"]\n',
        encoding="utf-8",
    )
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert "## Dependencies" in content
    assert "click" in content


def test_pipeline_injects_toc(proj_dir: Path) -> None:
    content = RenderPipeline(proj_dir).run(profile="rich")
    assert "## Contents" in content
