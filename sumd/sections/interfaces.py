"""sumd.sections.interfaces — InterfacesSection."""

from __future__ import annotations

from pathlib import Path

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_interfaces_openapi(
    openapi: dict, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    """Render REST API section into L (mutates in place)."""
    a = L.append
    a("### REST API (from `openapi.yaml`)")
    a("")
    if raw_sources:
        op_path = proj_dir / "openapi.yaml"
        if op_path.exists():
            a("```yaml markpact:openapi path=openapi.yaml")
            a(op_path.read_text(encoding="utf-8").rstrip())
            a("```")
            a("")
    else:
        a("| Method | Path | OperationId | Summary |")
        a("|--------|------|-------------|---------|")
        for ep in openapi["endpoints"]:
            summary = ep.get("summary", "").replace("|", "\\|")
            a(
                f"| `{ep['method']}` | `{ep['path']}` | `{ep['operationId']}` | {summary} |"
            )
        a("")
        if openapi.get("schemas"):
            a("**Schemas**: " + ", ".join(f"`{s}`" for s in openapi["schemas"]))
            a("")


def _render_testql_raw(scenarios: list, proj_dir: Path, L: list[str]) -> None:
    a = L.append
    seen_scenario_files: set[str] = set()
    for sc in scenarios:
        rel = sc.get("rel_path", sc["file"])
        fpath = proj_dir / rel
        if not fpath.exists() or rel in seen_scenario_files:
            continue
        seen_scenario_files.add(rel)
        a(f"#### `{rel}`")
        a("")
        a(f"```toon markpact:testql path={rel}")
        a(fpath.read_text(encoding="utf-8").rstrip())
        a("```")
        a("")


def _render_testql_endpoint(ep: dict, L: list[str]) -> None:
    """Render one endpoint line for a testql scenario."""
    op = f" — `{ep['operationId']}`" if ep.get("operationId") else ""
    sm = f": {ep['summary']}" if ep.get("summary") else ""
    L.append(f"  - `{ep['method']} {ep['path']}` → `{ep['status']}`{op}{sm}")


def _render_testql_extras(sc: dict, L: list[str]) -> None:
    """Render performance / navigate / gui blocks for a testql scenario."""
    a = L.append
    if sc.get("performance"):
        a("- **performance**:")
        for p in sc["performance"]:
            a(f"  - `{p['metric']} < {p['threshold']}`")
    if sc.get("navigate"):
        a("- **navigate**: " + ", ".join(f"`{u}`" for u in sc["navigate"]))
    if sc.get("gui"):
        a("- **gui actions**:")
        for g in sc["gui"]:
            a(f"  - `{g['action']} {g['selector']}`")


def _render_testql_one_structured(sc: dict, L: list[str]) -> None:
    a = L.append
    a(f"#### `{sc['file']}`")
    a("")
    a(f"- **name**: {sc['name']}")
    a(f"- **type**: `{sc['type']}`")
    if sc["detectors"]:
        a(f"- **detectors**: {sc['detectors']}")
    for k, v in sc["config"].items():
        a(f"- **{k}**: `{v}`")
    if sc["endpoints"]:
        a("- **endpoints**:")
        for ep in sc["endpoints"]:
            _render_testql_endpoint(ep, L)
    if sc["asserts"]:
        a("- **asserts**:")
        for ass in sc["asserts"]:
            a(f"  - `{ass['field']} {ass['op']} {ass['expected']}`")
    _render_testql_extras(sc, L)
    a("")


def _render_interfaces_testql(
    scenarios: list, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    """Render testql scenarios section into L (mutates in place)."""
    a = L.append
    a("### testql Scenarios")
    a("")
    if raw_sources:
        _render_testql_raw(scenarios, proj_dir, L)
    else:
        for sc in scenarios:
            _render_testql_one_structured(sc, L)


def _render_interfaces(
    scripts: list, openapi: dict, scenarios: list, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Interfaces")
    a("")
    if scripts:
        a("### CLI Entry Points")
        a("")
        for s in scripts:
            a(f"- `{s}`")
        a("")
    if openapi.get("endpoints"):
        _render_interfaces_openapi(openapi, proj_dir, raw_sources, L)
    if scenarios:
        _render_interfaces_testql(scenarios, proj_dir, raw_sources, L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class InterfacesSection:
    name = "interfaces"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.scripts or ctx.openapi.get("endpoints") or ctx.scenarios)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_interfaces(
            ctx.scripts, ctx.openapi, ctx.scenarios, ctx.proj_dir, ctx.raw_sources
        )


assert isinstance(InterfacesSection(), Section)
