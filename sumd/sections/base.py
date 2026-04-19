"""sumd.sections.base — RenderContext dataclass and Section Protocol.

RenderContext holds all extracted project data needed for rendering.
It is built once per project by RenderPipeline.run() and passed
immutably to every Section.render() call.

Section is a Protocol (structural typing) — no mandatory base class.
Implement the four attributes and two methods to register a section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# RenderContext — single immutable bag of all extracted project data
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RenderContext:
    """All extracted data for a project, passed to every Section.render()."""

    proj_dir: Path

    # pyproject.toml
    name: str = ""
    version: str = "0.0.0"
    description: str = ""
    py_req: str = ""
    license_: str = ""
    ai_model: str = ""
    deps: list = field(default_factory=list)
    dev_deps: list = field(default_factory=list)
    scripts: list = field(default_factory=list)

    # Extracted sources
    tasks: list = field(default_factory=list)
    scenarios: list = field(default_factory=list)
    openapi: dict = field(default_factory=dict)
    doql: dict = field(default_factory=dict)
    pyqual: dict = field(default_factory=dict)
    modules: list = field(default_factory=list)
    reqs: list = field(default_factory=list)
    makefile: list = field(default_factory=list)
    goal: dict = field(default_factory=dict)
    env_vars: list = field(default_factory=list)
    dockerfile: dict = field(default_factory=dict)
    compose: dict = field(default_factory=dict)
    pkg_json: dict = field(default_factory=dict)
    project_analysis: list = field(default_factory=list)
    source_snippets: list = field(default_factory=list)

    # Rendering options
    raw_sources: bool = True
    profile: str = "rich"

    # Derived
    sources_used: list = field(default_factory=list)
    title: str = ""


# ---------------------------------------------------------------------------
# Section Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class Section(Protocol):
    """Protocol for all SUMD section renderers.

    Attributes:
        name:     unique identifier used in PROFILES dict
        level:    markdown heading level (2 = ##, 3 = ###)
        profiles: which profiles include this section

    Methods:
        should_render: return False to skip section (e.g. no data)
        render:        return rendered markdown lines (NOT joined)
    """

    name: str
    level: int
    profiles: frozenset[str]

    def should_render(self, ctx: RenderContext) -> bool: ...
    def render(self, ctx: RenderContext) -> list[str]: ...


__all__ = ["RenderContext", "Section"]
