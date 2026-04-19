"""sumd.sections.test_contracts — TestContractsSection.

Renders testql scenarios as contract signatures: endpoint + key assertions.
LLM sees what the system guarantees without reading full scenario files.
"""

from __future__ import annotations

from sumd.renderer import _render_test_contracts
from sumd.sections.base import RenderContext, Section


class TestContractsSection:
    name = "test_contracts"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.scenarios)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_test_contracts(ctx.scenarios)


assert isinstance(TestContractsSection(), Section)
