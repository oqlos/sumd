"""sumd.sections.metadata — MetadataSection.

Renders the ## Metadata block. Maps 1:1 to the existing
_render_metadata_section() in renderer.py so output is bit-identical.
This serves as the reference implementation for all other sections.
"""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


class MetadataSection:
    """Render ## Metadata — always present, all profiles."""

    name: str = "metadata"
    level: int = 2
    profiles: frozenset[str] = frozenset({"minimal", "light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return True  # Always render

    def render(self, ctx: RenderContext) -> list[str]:
        L: list[str] = []
        a = L.append
        a("## Metadata")
        a("")
        a(f"- **name**: `{ctx.name}`")
        a(f"- **version**: `{ctx.version}`")
        if ctx.py_req:
            a(f"- **python_requires**: `{ctx.py_req}`")
        if ctx.license_:
            a(f"- **license**: {ctx.license_}")
        if ctx.ai_model:
            a(f"- **ai_model**: `{ctx.ai_model}`")
        a("- **ecosystem**: SUMD + DOQL + testql + taskfile")
        if ctx.openapi.get("title"):
            a(
                f"- **openapi_title**: {ctx.openapi['title']} v{ctx.openapi.get('version', '')}"
            )
        a(f"- **generated_from**: {', '.join(ctx.sources_used)}")
        a("")
        return L


# Verify the class satisfies the Section protocol at import time
assert isinstance(MetadataSection(), Section), (
    "MetadataSection does not satisfy Section protocol"
)

__all__ = ["MetadataSection"]
