"""sumd.sections.workflows — WorkflowsSection."""
from __future__ import annotations

from sumd.renderer import _render_workflows
from sumd.sections.base import RenderContext, Section


class WorkflowsSection:
    name = "workflows"
    level = 2
    profiles = frozenset({"minimal", "light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.tasks or ctx.doql.get("workflows"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_workflows(ctx.doql, ctx.tasks, ctx.proj_dir, ctx.raw_sources)


assert isinstance(WorkflowsSection(), Section)
