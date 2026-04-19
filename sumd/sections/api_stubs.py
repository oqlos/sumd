"""sumd.sections.api_stubs — ApiStubsSection.

Renders OpenAPI endpoints as Python-like typed stubs for LLM orientation.
LLM sees function signatures and HTTP method/path without reading full openapi.yaml.
"""

from __future__ import annotations

from sumd.renderer import _render_api_stubs
from sumd.sections.base import RenderContext, Section


class ApiStubsSection:
    name = "api_stubs"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.openapi.get("endpoints"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_api_stubs(ctx.openapi)


assert isinstance(ApiStubsSection(), Section)
