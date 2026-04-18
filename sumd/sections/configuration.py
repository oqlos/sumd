"""sumd.sections.configuration — ConfigurationSection."""
from __future__ import annotations

from sumd.renderer import _render_configuration_section
from sumd.sections.base import RenderContext, Section


class ConfigurationSection:
    name = "configuration"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return True

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_configuration_section(ctx.name, ctx.version)


assert isinstance(ConfigurationSection(), Section)
