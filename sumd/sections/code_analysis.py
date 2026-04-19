"""sumd.sections.code_analysis — CodeAnalysisSection."""

from __future__ import annotations

from sumd.renderer import _render_code_analysis
from sumd.sections.base import RenderContext, Section


class CodeAnalysisSection:
    name = "code_analysis"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        # Skip if ALL entries are calls.toon (handled by CallGraphSection)
        non_calls = [
            e for e in ctx.project_analysis if "calls.toon" not in e.get("file", "")
        ]
        return bool(non_calls)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_code_analysis(ctx.project_analysis, skip_files={"calls.toon"})


assert isinstance(CodeAnalysisSection(), Section)
