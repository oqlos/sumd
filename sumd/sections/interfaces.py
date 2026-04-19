"""sumd.sections.interfaces — InterfacesSection."""

from __future__ import annotations

from sumd.renderer import _render_interfaces
from sumd.sections.base import RenderContext, Section


class InterfacesSection:
    name = "interfaces"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.scripts or ctx.openapi.get("endpoints") or ctx.scenarios)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_interfaces(
            ctx.scripts, ctx.openapi, ctx.scenarios, ctx.proj_dir, ctx.raw_sources
        )


assert isinstance(InterfacesSection(), Section)
