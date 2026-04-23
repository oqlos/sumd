"""sumd.sections.environment — EnvironmentSection (env vars + goal/release)."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_env_section(env_vars: list) -> list[str]:
    if not env_vars:
        return []
    L: list[str] = []
    a = L.append
    a("## Environment Variables (`.env.example`)")
    a("")
    a("| Variable | Default | Description |")
    a("|----------|---------|-------------|")
    for v in env_vars:
        desc = v["comment"].replace("|", "\\|")
        a(f"| `{v['key']}` | `{v['default']}` | {desc} |")
    a("")
    return L


def _render_goal_section(goal: dict) -> list[str]:
    if not goal.get("name"):
        return []
    L: list[str] = []
    a = L.append
    a("## Release Management (`goal.yaml`)")
    a("")
    if goal.get("versioning_strategy"):
        a(f"- **versioning**: `{goal['versioning_strategy']}`")
    if goal.get("commit_strategy"):
        a(
            f"- **commits**: `{goal['commit_strategy']}` scope=`{goal.get('commit_scope', '')}`"
        )
    if goal.get("changelog_template"):
        a(f"- **changelog**: `{goal['changelog_template']}`")
    if goal.get("strategies"):
        a(f"- **build strategies**: {', '.join(f'`{s}`' for s in goal['strategies'])}")
    if goal.get("version_files"):
        a(f"- **version files**: {', '.join(f'`{f}`' for f in goal['version_files'])}")
    a("")
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class EnvironmentSection:
    name = "environment"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.env_vars or ctx.goal.get("name"))

    def render(self, ctx: RenderContext) -> list[str]:
        lines: list[str] = []
        lines.extend(_render_env_section(ctx.env_vars))
        lines.extend(_render_goal_section(ctx.goal))
        return lines


assert isinstance(EnvironmentSection(), Section)
