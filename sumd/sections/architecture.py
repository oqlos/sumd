"""sumd.sections.architecture — ArchitectureSection."""
from __future__ import annotations

from sumd.renderer import _render_architecture
from sumd.sections.base import RenderContext, Section


class ArchitectureSection:
    name = "architecture"
    level = 2
    profiles = frozenset({"minimal", "light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return True

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_architecture(ctx.doql, ctx.modules, ctx.name, ctx.proj_dir, ctx.raw_sources)


assert isinstance(ArchitectureSection(), Section)
