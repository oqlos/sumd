"""sumd.sections.environment — EnvironmentSection (env vars + goal/release)."""
from __future__ import annotations

from sumd.renderer import _render_env_section, _render_goal_section
from sumd.sections.base import RenderContext, Section


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
