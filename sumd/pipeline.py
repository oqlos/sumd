"""sumd.pipeline — RenderPipeline: collect → build_sections → render → toc.

RenderPipeline is the new entry point for SUMD generation.
It replaces the monolithic generate_sumd_content() but currently runs
alongside it — generate_sumd_content() is unchanged and still works.

CURRENT STATE (Faza 1 scaffold):
  Only MetadataSection is registered. Other sections fall back to the
  existing _render_* functions in renderer.py (via _render_legacy_sections).
  This approach allows incremental migration one section at a time — each
  section can be extracted without breaking the output.

MIGRATION PATH:
  1. Add new Section class to sumd/sections/
  2. Add to SECTION_REGISTRY in sumd/sections/__init__.py
  3. Remove the corresponding _render_* call from _render_legacy_sections()
  4. Verify output is bit-identical, tests pass

ACCEPTANCE (Faza 1 complete):
  _render_legacy_sections() is empty, generate_sumd_content() is a thin
  wrapper calling RenderPipeline.run(profile='rich').
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from sumd.extractor import (
    extract_docker_compose,
    extract_dockerfile,
    extract_doql,
    extract_env,
    extract_goal,
    extract_makefile,
    extract_openapi,
    extract_package_json,
    extract_project_analysis,
    extract_pyproject,
    extract_pyqual,
    extract_python_modules,
    extract_readme_title,
    extract_requirements,
    extract_source_snippets,
    extract_taskfile,
    generate_map_toon,
    required_tools_for_profile,
)
from sumd.renderer import (
    _collect_sources,
    _inject_toc,
)
from sumd.sections import PROFILES, SECTION_REGISTRY
from sumd.sections.base import RenderContext
from sumd.toon_parser import extract_testql_scenarios


def _refresh_map_toon(proj_dir: Path) -> None:
    """Regenerate project/map.toon.yaml from current source before embedding.

    Called automatically by RenderPipeline._collect() so that every
    `sumd scan` / `sumd .` / `sumr .` embeds an up-to-date map regardless
    of whether the user ran `sumd map` manually beforehand.

    Silently skips if generation fails (e.g. no Python sources found).
    """
    try:
        content = generate_map_toon(proj_dir)
        if not content:
            return
        map_path = proj_dir / "project" / "map.toon.yaml"
        map_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.write_text(content, encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass  # non-fatal — embed will use the previous file if it exists


def _find_tools_bin_dir(proj_dir: Path) -> Path | None:
    """Return the venv bin directory for .sumd-tools, or None if not installed."""
    base = proj_dir / ".sumd-tools" / "venv"
    for subdir in ("bin", "Scripts"):
        candidate = base / subdir
        if candidate.exists():
            return candidate
    return None


def _run_tool_if_present(bin_dir: Path, name: str, args: list, proj_dir: Path) -> None:
    """Run *name* executable with *args* if it exists in *bin_dir*."""
    exe = bin_dir / name
    if not exe.exists():
        exe = bin_dir / f"{name}.exe"
    if exe.exists():
        subprocess.run([str(exe)] + args, capture_output=True, cwd=str(proj_dir))


def _refresh_analysis_files(proj_dir: Path, profile: str) -> None:
    """Run only the external tools required for the given profile.

    Called from RenderPipeline._collect() before extract_project_analysis()
    so analysis files are always fresh when embedded.  Silently skips any
    tool not installed in .sumd-tools/venv.

    profile: 'minimal' | 'light' | 'rich' | 'refactor'
    """
    tools_needed = required_tools_for_profile(profile)
    if not tools_needed:
        return

    bin_dir = _find_tools_bin_dir(proj_dir)
    if not bin_dir:
        return  # tools not installed — skip silently

    project_output = proj_dir / "project"
    project_output.mkdir(parents=True, exist_ok=True)

    try:
        if "code2llm" in tools_needed:
            _run_tool_if_present(
                bin_dir, "code2llm",
                ["./", "-f", "toon", "-o", str(project_output), "--no-chunk"],
                proj_dir,
            )
        if "redup" in tools_needed:
            _run_tool_if_present(
                bin_dir, "redup",
                ["scan", str(proj_dir), "--format", "toon", "--output", str(project_output)],
                proj_dir,
            )
        if "vallm" in tools_needed:
            _run_tool_if_present(
                bin_dir, "vallm",
                ["batch", str(proj_dir), "--recursive",
                 "--format", "toon", "--output", str(project_output)],
                proj_dir,
            )
    except Exception:  # noqa: BLE001
        pass  # non-fatal


class RenderPipeline:
    """Collect project data → build sections → render → inject TOC.

    Usage:
        pipeline = RenderPipeline(proj_dir)
        content, sources = pipeline.run(profile='rich', return_sources=True)
    """

    def __init__(self, proj_dir: Path, raw_sources: bool = True) -> None:
        self.proj_dir = proj_dir.resolve()
        self.raw_sources = raw_sources
        self._profile: str = "rich"  # set before _collect() by run()

    # ── Phase 1: collect ────────────────────────────────────────────────

    def _collect(self) -> RenderContext:
        """Extract all project data and build RenderContext."""
        proj_dir = self.proj_dir
        pkg_name = proj_dir.name

        pyproj = extract_pyproject(proj_dir)
        tasks = extract_taskfile(proj_dir)
        scenarios = extract_testql_scenarios(proj_dir)
        openapi = extract_openapi(proj_dir)
        doql = extract_doql(proj_dir)
        pyqual = extract_pyqual(proj_dir)
        modules = extract_python_modules(proj_dir, pkg_name)
        title = extract_readme_title(proj_dir)
        reqs = extract_requirements(proj_dir)
        makefile = extract_makefile(proj_dir)
        goal = extract_goal(proj_dir)
        env_vars = extract_env(proj_dir)
        dockerfile = extract_dockerfile(proj_dir)
        compose = extract_docker_compose(proj_dir)
        pkg_json = extract_package_json(proj_dir)

        # Auto-regenerate map.toon.yaml — pure-Python, always fast.
        _refresh_map_toon(proj_dir)

        # Run only the external tools needed by the active profile (if installed).
        _refresh_analysis_files(proj_dir, self._profile)

        project_analysis = extract_project_analysis(
            proj_dir, refactor=(self._profile == "refactor")
        )
        source_snippets = extract_source_snippets(proj_dir, pkg_name)

        name = pyproj.get("name", pkg_name)
        version = pyproj.get("version", "0.0.0")
        description = pyproj.get("description", title or name)
        sources_used = _collect_sources(
            pyproj,
            reqs,
            tasks,
            makefile,
            scenarios,
            openapi,
            doql,
            pyqual,
            goal,
            env_vars,
            dockerfile,
            compose,
            pkg_json,
            modules,
            project_analysis,
        )

        return RenderContext(
            proj_dir=proj_dir,
            name=name,
            version=version,
            description=description,
            py_req=pyproj.get("python_requires", ""),
            license_=pyproj.get("license", ""),
            ai_model=pyproj.get("ai_model", ""),
            deps=pyproj.get("dependencies", []),
            dev_deps=pyproj.get("dev_dependencies", []),
            scripts=pyproj.get("scripts", []),
            tasks=tasks,
            scenarios=scenarios,
            openapi=openapi,
            doql=doql,
            pyqual=pyqual,
            modules=modules,
            reqs=reqs,
            makefile=makefile,
            goal=goal,
            env_vars=env_vars,
            dockerfile=dockerfile,
            compose=compose,
            pkg_json=pkg_json,
            project_analysis=project_analysis,
            source_snippets=source_snippets,
            raw_sources=self.raw_sources,
            sources_used=sources_used,
            title=title or name,
        )

    # ── Phase 2: build sections ─────────────────────────────────────────

    def _build_registered_sections(
        self, ctx: RenderContext, profile: str
    ) -> list[list[str]]:
        """Run all registered Section classes that match the profile."""
        allowed = PROFILES.get(profile, set())
        rendered: list[list[str]] = []
        for cls in SECTION_REGISTRY:
            section = cls()
            if section.name not in allowed:
                continue
            if not section.should_render(ctx):
                continue
            rendered.append(section.render(ctx))
        return rendered

    def _render_legacy_sections(self, ctx: RenderContext) -> list[list[str]]:
        """All sections have been migrated to Section classes. Returns empty list."""
        return []

    # ── Phase 3: render ─────────────────────────────────────────────────

    def _assemble(self, ctx: RenderContext, profile: str) -> str:
        """Assemble all section lines into final markdown."""
        L: list[str] = []
        a = L.append

        # Document header
        a(f"# {ctx.title}")
        a("")
        if profile == "refactor":
            a(
                "SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization"
            )
        else:
            a(ctx.description)
        a("")

        # Registered sections (new architecture)
        for section_lines in self._build_registered_sections(ctx, profile):
            L.extend(section_lines)

        # Intent section (inline — will become IntentSection later)
        a("## Intent")
        a("")
        a(ctx.description)
        a("")

        # Legacy sections (not yet migrated)
        for section_lines in self._render_legacy_sections(ctx):
            L.extend(section_lines)

        return "\n".join(L)

    # ── Public API ───────────────────────────────────────────────────────

    def run(
        self, profile: str = "rich", return_sources: bool = False
    ) -> str | tuple[str, list[str]]:
        """Run the full pipeline and return rendered SUMD content.

        Args:
            profile: 'minimal' | 'light' | 'rich' | 'refactor'
            return_sources: if True, return (content, sources_used) tuple

        Returns:
            str or (str, list[str])
        """
        self._profile = profile
        ctx = self._collect()
        raw = self._assemble(ctx, profile)
        content = _inject_toc(raw)

        if return_sources:
            return content, ctx.sources_used
        return content


__all__ = ["RenderPipeline"]
