"""sumd.sections.dependencies — DependenciesSection."""

from __future__ import annotations

from sumd.renderer import _render_dependencies
from sumd.sections.base import RenderContext, Section


class DependenciesSection:
    name = "dependencies"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(
            ctx.deps
            or ctx.dev_deps
            or ctx.pkg_json.get("dependencies")
            or ctx.pkg_json.get("devDependencies")
        )

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_dependencies(ctx.deps, ctx.dev_deps, ctx.pkg_json)


assert isinstance(DependenciesSection(), Section)
