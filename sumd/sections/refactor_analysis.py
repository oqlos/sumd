"""sumd.sections.refactor_analysis — RefactorAnalysisSection.

Renders a pre-refactoring analysis report from project/ toon files:
  - calls.toon.yaml   — call graph with CC/fan metrics
  - analysis.toon.yaml — code quality / complexity scan
  - duplication.toon.yaml — duplicate code blocks
  - evolution.toon.yaml — change history / churn
  - validation.toon.yaml — lint / type / test results

Only active in the 'refactor' profile. map.toon.yaml is intentionally
excluded — the structural overview is less relevant for refactoring context;
calls.toon.yaml already captures the graph.

Files that don't exist are silently skipped (non-blocking).
"""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section

# Display order and labels for refactor analysis files.
_REFACTOR_FILE_LABELS: dict[str, str] = {
    "calls.toon.yaml": "Call Graph & Complexity",
    "analysis.toon.yaml": "Code Analysis",
    "duplication.toon.yaml": "Duplication",
    "evolution.toon.yaml": "Evolution / Churn",
    "validation.toon.yaml": "Validation",
}

# map.toon.yaml is available in project_analysis for refactor profile but
# intentionally not listed here — structural map is part of Architecture section.


class RefactorAnalysisSection:
    name = "refactor_analysis"
    level = 2
    profiles = frozenset({"refactor"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.project_analysis)

    def render(self, ctx: RenderContext) -> list[str]:
        L: list[str] = []
        a = L.append
        a("## Refactoring Analysis")
        a("")
        a(
            "*Pre-refactoring snapshot — use this section to identify targets. "
            "Generated from `project/` toon files.*"
        )
        a("")

        for entry in ctx.project_analysis:
            fname = entry["file"].replace("project/", "", 1)
            if fname not in _REFACTOR_FILE_LABELS:
                continue
            label = _REFACTOR_FILE_LABELS[fname]
            a(f"### {label} (`{entry['file']}`)")
            a("")
            a(f"```toon markpact:analysis path={entry['file']}")
            a(entry["content"])
            a("```")
            a("")

        return L


assert isinstance(RefactorAnalysisSection(), Section)
