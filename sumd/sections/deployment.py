"""sumd.sections.deployment — DeploymentSection."""

from __future__ import annotations

from sumd.renderer import _render_deployment
from sumd.sections.base import RenderContext, Section


class DeploymentSection:
    name = "deployment"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return True

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_deployment(
            ctx.pkg_json, ctx.name, ctx.reqs, ctx.dockerfile, ctx.compose
        )


assert isinstance(DeploymentSection(), Section)
