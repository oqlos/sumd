"""sumd.sections.extras — ExtrasSection (Makefile + package.json scripts)."""

from __future__ import annotations

from sumd.renderer import _render_extras
from sumd.sections.base import RenderContext, Section


class ExtrasSection:
    name = "extras"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.makefile or ctx.pkg_json.get("scripts"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_extras(ctx.makefile, ctx.pkg_json)


assert isinstance(ExtrasSection(), Section)
