"""sumd.sections.code_analysis — CodeAnalysisSection."""
from __future__ import annotations

from sumd.renderer import _render_code_analysis
from sumd.sections.base import RenderContext, Section


class CodeAnalysisSection:
    name = "code_analysis"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.project_analysis)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_code_analysis(ctx.project_analysis)


assert isinstance(CodeAnalysisSection(), Section)
