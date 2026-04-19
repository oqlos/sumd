"""sumd.sections.quality — QualitySection."""

from __future__ import annotations

from sumd.renderer import _render_quality
from sumd.sections.base import RenderContext, Section


class QualitySection:
    name = "quality"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.pyqual)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_quality(ctx.pyqual, ctx.proj_dir, ctx.raw_sources)


assert isinstance(QualitySection(), Section)
