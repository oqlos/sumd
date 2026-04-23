"""sumd.sections.workflows — WorkflowsSection."""

from __future__ import annotations

from pathlib import Path

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_workflows_doql(doql: dict, L: list[str]) -> None:
    a = L.append
    doql_sources_wf = ", ".join(
        f"`{s}`" for s in doql.get("sources", ["app.doql.less"])
    )
    a(f"### DOQL Workflows ({doql_sources_wf})")
    a("")
    for wf in doql["workflows"]:
        steps = " → ".join(wf["steps"]) if wf["steps"] else "*(no steps)*"
        a(f"- **{wf['name']}** `[{wf['trigger']}]`: `{steps}`")
    a("")


def _render_workflows_taskfile(
    tasks: list, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    a = L.append
    a("### Taskfile Tasks (`Taskfile.yml`)")
    a("")
    if raw_sources:
        taskfile_path = proj_dir / "Taskfile.yml"
        if taskfile_path.exists():
            a("```yaml markpact:taskfile path=Taskfile.yml")
            a(taskfile_path.read_text(encoding="utf-8").rstrip())
            a("```")
            a("")
    else:
        a("```yaml markpact:taskfile path=Taskfile.yml")
        a("tasks:")
        for t in tasks:
            a(f"  {t['name']}:")
            if t["desc"]:
                a(f'    desc: "{t["desc"]}"')
            if t["cmd"]:
                a("    cmds:")
                a(f"      - {t['cmd']}")
        a("```")
        a("")


def _render_workflows(
    doql: dict, tasks: list, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Workflows")
    a("")
    if doql.get("workflows") and not raw_sources:
        _render_workflows_doql(doql, L)
    if tasks:
        _render_workflows_taskfile(tasks, proj_dir, raw_sources, L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class WorkflowsSection:
    name = "workflows"
    level = 2
    profiles = frozenset({"minimal", "light", "rich", "refactor"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.tasks or ctx.doql.get("workflows"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_workflows(ctx.doql, ctx.tasks, ctx.proj_dir, ctx.raw_sources)


assert isinstance(WorkflowsSection(), Section)
