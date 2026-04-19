"""sumd.sections.source_snippets — SourceSnippetsSection.

Renders top-N modules with function/class signatures for LLM orientation.
Gives the model a structural map of the codebase without requiring it
to read full source files.
"""

from __future__ import annotations

from sumd.renderer import _render_source_snippets
from sumd.sections.base import RenderContext, Section


class SourceSnippetsSection:
    name = "source_snippets"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.source_snippets)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_source_snippets(ctx.source_snippets)


assert isinstance(SourceSnippetsSection(), Section)
