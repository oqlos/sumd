"""Tests for all Section classes — should_render + render output."""

from __future__ import annotations

from pathlib import Path


from sumd.sections.base import RenderContext
from sumd.sections.metadata import MetadataSection
from sumd.sections.architecture import ArchitectureSection
from sumd.sections.dependencies import DependenciesSection
from sumd.sections.workflows import WorkflowsSection
from sumd.sections.quality import QualitySection
from sumd.sections.environment import EnvironmentSection
from sumd.sections.call_graph import CallGraphSection
from sumd.sections.code_analysis import CodeAnalysisSection
from sumd.sections.source_snippets import SourceSnippetsSection
from sumd.sections.refactor_analysis import RefactorAnalysisSection


def make_ctx(**kwargs) -> RenderContext:
    """Build a minimal RenderContext with sensible defaults."""
    defaults = dict(
        proj_dir=Path("/tmp/fake"),
        name="mypkg",
        version="1.0.0",
        description="A test package",
        raw_sources=False,
    )
    defaults.update(kwargs)
    return RenderContext(**defaults)


# ── MetadataSection ──────────────────────────────────────────────────────────


class TestMetadataSection:
    def test_always_renders(self):
        ctx = make_ctx()
        assert MetadataSection().should_render(ctx) is True

    def test_contains_name_and_version(self):
        ctx = make_ctx(name="myapp", version="2.3.4")
        lines = MetadataSection().render(ctx)
        joined = "\n".join(lines)
        assert "myapp" in joined
        assert "2.3.4" in joined

    def test_contains_metadata_header(self):
        lines = MetadataSection().render(make_ctx())
        assert lines[0] == "## Metadata"

    def test_optional_fields_omitted_when_empty(self):
        ctx = make_ctx(license_="", ai_model="")
        lines = MetadataSection().render(ctx)
        joined = "\n".join(lines)
        assert "- **license**" not in joined


# ── ArchitectureSection ──────────────────────────────────────────────────────


class TestArchitectureSection:
    def test_always_renders(self):
        assert ArchitectureSection().should_render(make_ctx()) is True

    def test_header_present(self):
        lines = ArchitectureSection().render(make_ctx())
        assert any("## Architecture" in line for line in lines)

    def test_modules_listed(self):
        ctx = make_ctx(modules=["core", "utils"], name="mypkg")
        lines = ArchitectureSection().render(ctx)
        joined = "\n".join(lines)
        assert "mypkg.core" in joined
        assert "mypkg.utils" in joined

    def test_no_modules_no_source_modules_section(self):
        ctx = make_ctx(modules=[], doql={})
        lines = ArchitectureSection().render(ctx)
        joined = "\n".join(lines)
        assert "Source Modules" not in joined


# ── DependenciesSection ──────────────────────────────────────────────────────


class TestDependenciesSection:
    def test_renders_when_deps_present(self):
        assert DependenciesSection().should_render(make_ctx(deps=["click"])) is True

    def test_runtime_deps_listed(self):
        ctx = make_ctx(deps=["click>=8.0", "pyyaml>=6.0"])
        lines = DependenciesSection().render(ctx)
        joined = "\n".join(lines)
        assert "click" in joined
        assert "pyyaml" in joined

    def test_no_deps_shows_fallback(self):
        ctx = make_ctx(deps=[], dev_deps=[])
        lines = DependenciesSection().render(ctx)
        joined = "\n".join(lines)
        assert "pyproject.toml" in joined

    def test_dev_deps_section(self):
        ctx = make_ctx(deps=[], dev_deps=["pytest>=7.0", "ruff"])
        lines = DependenciesSection().render(ctx)
        joined = "\n".join(lines)
        assert "Development" in joined
        assert "pytest" in joined


# ── WorkflowsSection ─────────────────────────────────────────────────────────


class TestWorkflowsSection:
    def test_no_render_when_empty(self):
        ctx = make_ctx(tasks=[], doql={})
        assert WorkflowsSection().should_render(ctx) is False

    def test_renders_with_tasks(self):
        ctx = make_ctx(tasks=[{"name": "test", "desc": "Run tests", "cmd": "pytest"}])
        assert WorkflowsSection().should_render(ctx) is True
        lines = WorkflowsSection().render(ctx)
        joined = "\n".join(lines)
        assert "test" in joined

    def test_header_present(self):
        ctx = make_ctx(tasks=[{"name": "build", "desc": "", "cmd": "make"}])
        lines = WorkflowsSection().render(ctx)
        assert lines[0] == "## Workflows"


# ── QualitySection ───────────────────────────────────────────────────────────


class TestQualitySection:
    def test_no_render_when_empty(self):
        assert QualitySection().should_render(make_ctx(pyqual={})) is False

    def test_renders_with_pyqual(self):
        ctx = make_ctx(
            pyqual={"name": "quality-loop", "stages": [], "metrics": {}, "loop": {}}
        )
        assert QualitySection().should_render(ctx) is True

    def test_pipeline_name_in_output(self):
        ctx = make_ctx(
            pyqual={"name": "my-pipeline", "stages": [], "metrics": {}, "loop": {}},
            raw_sources=False,
        )
        lines = QualitySection().render(ctx)
        joined = "\n".join(lines)
        assert "my-pipeline" in joined


# ── EnvironmentSection ────────────────────────────────────────────────────────


class TestEnvironmentSection:
    def test_no_render_when_empty(self):
        assert EnvironmentSection().should_render(make_ctx(env_vars=[])) is False

    def test_renders_with_vars(self):
        ctx = make_ctx(
            env_vars=[{"key": "API_KEY", "default": "", "comment": "API key"}]
        )
        assert EnvironmentSection().should_render(ctx) is True
        lines = EnvironmentSection().render(ctx)
        assert any("API_KEY" in line for line in lines)


# ── CallGraphSection ─────────────────────────────────────────────────────────


class TestCallGraphSection:
    def test_no_render_without_calls(self):
        ctx = make_ctx(project_analysis=[])
        assert CallGraphSection().should_render(ctx) is False

    def test_no_render_without_calls_file(self):
        ctx = make_ctx(
            project_analysis=[
                {"file": "project/map.toon.yaml", "lang": "toon", "content": "x"}
            ]
        )
        assert CallGraphSection().should_render(ctx) is False

    def test_renders_with_calls_file(self):
        ctx = make_ctx(
            project_analysis=[
                {
                    "file": "project/calls.toon.yaml",
                    "lang": "toon",
                    "content": "HUBS[1]:\n  mod.func\n    CC=3  in:0  out:2  total:2\n",
                }
            ]
        )
        assert CallGraphSection().should_render(ctx) is True
        lines = CallGraphSection().render(ctx)
        assert any("Call Graph" in line for line in lines)


# ── CodeAnalysisSection ───────────────────────────────────────────────────────


class TestCodeAnalysisSection:
    def test_no_render_when_only_calls(self):
        ctx = make_ctx(
            project_analysis=[
                {"file": "project/calls.toon.yaml", "lang": "toon", "content": "x"}
            ]
        )
        assert CodeAnalysisSection().should_render(ctx) is False

    def test_renders_with_map(self):
        ctx = make_ctx(
            project_analysis=[
                {
                    "file": "project/map.toon.yaml",
                    "lang": "toon",
                    "content": "MAP content",
                }
            ]
        )
        assert CodeAnalysisSection().should_render(ctx) is True


# ── RefactorAnalysisSection ───────────────────────────────────────────────────


class TestRefactorAnalysisSection:
    def test_no_render_when_empty(self):
        assert (
            RefactorAnalysisSection().should_render(make_ctx(project_analysis=[]))
            is False
        )

    def test_renders_with_analysis_files(self):
        ctx = make_ctx(
            project_analysis=[
                {
                    "file": "project/calls.toon.yaml",
                    "lang": "toon",
                    "content": "HUBS[0]:",
                },
                {
                    "file": "project/analysis.toon.yaml",
                    "lang": "toon",
                    "content": "METRICS:",
                },
            ]
        )
        assert RefactorAnalysisSection().should_render(ctx) is True
        lines = RefactorAnalysisSection().render(ctx)
        joined = "\n".join(lines)
        assert "## Refactoring Analysis" in joined
        assert "Call Graph" in joined
        assert "Code Analysis" in joined

    def test_map_toon_excluded(self):
        """map.toon.yaml should not appear in refactoring analysis section."""
        ctx = make_ctx(
            project_analysis=[
                {"file": "project/map.toon.yaml", "lang": "toon", "content": "MAP"}
            ]
        )
        lines = RefactorAnalysisSection().render(ctx)
        joined = "\n".join(lines)
        assert "map.toon.yaml" not in joined


# ── SourceSnippetsSection ─────────────────────────────────────────────────────


class TestSourceSnippetsSection:
    def test_no_render_when_empty(self):
        assert (
            SourceSnippetsSection().should_render(make_ctx(source_snippets=[])) is False
        )

    def test_renders_with_snippets(self):
        ctx = make_ctx(
            source_snippets=[
                {
                    "module": "mypkg.core",
                    "path": "mypkg/core.py",
                    "funcs": [{"name": "run", "args": [], "cc": 1, "fan": 2}],
                    "classes": [],
                }
            ]
        )
        assert SourceSnippetsSection().should_render(ctx) is True
        lines = SourceSnippetsSection().render(ctx)
        joined = "\n".join(lines)
        assert "mypkg.core" in joined
        assert "run" in joined
