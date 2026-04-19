"""sumd.sections.call_graph — CallGraphSection.

Renders a summary of the call graph (HUBS table + degree stats) from
calls.toon.yaml in project/, followed by the full embed for LLM reference.

Replaces the raw dump that would otherwise appear in CodeAnalysis.
"""

from __future__ import annotations

from sumd.renderer import _render_call_graph
from sumd.sections.base import RenderContext, Section


class CallGraphSection:
    name = "call_graph"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return any("calls.toon" in e.get("file", "") for e in ctx.project_analysis)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_call_graph(ctx.project_analysis)


assert isinstance(CallGraphSection(), Section)
