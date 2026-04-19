"""renderer — render SUMD.md content from extracted project metadata."""

from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Section renderers (private) — each returns list[str] lines
# ---------------------------------------------------------------------------


def _render_architecture_doql_section(
    doql: dict, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    a = L.append
    doql_sources = ", ".join(f"`{s}`" for s in doql.get("sources", ["app.doql.less"]))
    a(f"### DOQL Application Declaration ({doql_sources})")
    a("")
    if raw_sources:
        for fname in doql.get("sources", ["app.doql.less"]):
            fpath = proj_dir / fname
            if fpath.exists():
                lang = "less" if fname.endswith(".less") else "css"
                a(f"```{lang} markpact:doql path={fname}")
                a(fpath.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
    else:
        _render_architecture_doql_parsed(doql, L)


def _render_architecture_modules(modules: list[str], name: str, L: list[str]) -> None:
    a = L.append
    a("### Source Modules")
    a("")
    for mod in modules:
        a(f"- `{name}.{mod}`")
    a("")


def _render_architecture(
    doql: dict, modules: list[str], name: str, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Architecture")
    a("")
    a("```")
    a(
        "SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)"
    )
    a("```")
    a("")
    if (
        doql.get("app")
        or doql.get("entities")
        or doql.get("interfaces")
        or doql.get("workflows")
    ):
        _render_architecture_doql_section(doql, proj_dir, raw_sources, L)
    if modules:
        _render_architecture_modules(modules, name, L)
    return L


def _render_doql_app(doql: dict, L: list[str]) -> None:
    if not doql.get("app"):
        return
    a = L.append
    a("```less")
    a("app {")
    for k, v in doql["app"].items():
        a(f"  {k}: {v};")
    a("}")
    a("```")
    a("")


def _render_doql_entities(doql: dict, L: list[str]) -> None:
    if not doql.get("entities"):
        return
    a = L.append
    a("### DOQL Data Model (`entity`)")
    a("")
    for ent in doql["entities"]:
        attrs_str = ""
        if ent.get("attrs"):
            attrs_str = " — " + ", ".join(
                f"`{k}: {v}`" for k, v in ent["attrs"].items()
            )
        page_str = f" page=`{ent['page']}`" if ent.get("page") else ""
        a(f"- `entity[{ent['name']}]`{page_str}{attrs_str}")
    a("")


def _render_doql_interfaces(doql: dict, L: list[str]) -> None:
    if not doql.get("interfaces"):
        return
    a = L.append
    a("### DOQL Interfaces")
    a("")
    for iface in list(doql["interfaces"]):
        sel = iface.get("selector", "")
        attrs = ", ".join(
            f"{k}: {v}" for k, v in iface.items() if k not in ("selector", "page")
        )
        page_str = f" page=`{iface['page']}`" if iface.get("page") else ""
        a(f"- `interface[{sel}]`{page_str} — {attrs}")
    a("")


def _render_doql_integrations(doql: dict, L: list[str]) -> None:
    if not doql.get("integrations"):
        return
    a = L.append
    a("### DOQL Integrations")
    a("")
    for intg in list(doql["integrations"]):
        sel = intg.get("selector", "")
        attrs = ", ".join(f"{k}: {v}" for k, v in intg.items() if k != "selector")
        a(f"- `integration[{sel}]` — {attrs}")
    a("")


def _render_architecture_doql_parsed(doql: dict, L: list[str]) -> None:
    """Render parsed DOQL blocks into L (mutates in place)."""
    _render_doql_app(doql, L)
    _render_doql_entities(doql, L)
    _render_doql_interfaces(doql, L)
    _render_doql_integrations(doql, L)


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


def _render_workflows_doql(doql: dict, L: list[str]) -> None:
    a = L.append
    doql_sources_wf = ", ".join(
        f"`{s}`" for s in doql.get("sources", ["app.doql.less"])
    )
    a(f"### DOQL Workflows ({doql_sources_wf})")
    a("")
    for wf in doql["workflows"]:
        steps = " → ".join(wf["steps"]) if wf["steps"] else "*(no steps)*"
        a(f"- **{wf['name']}** `[{wf['trigger']}]`: `{steps}`")
    a("")


def _render_workflows_taskfile(
    tasks: list, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    a = L.append
    a("### Taskfile Tasks (`Taskfile.yml`)")
    a("")
    if raw_sources:
        taskfile_path = proj_dir / "Taskfile.yml"
        if taskfile_path.exists():
            a("```yaml markpact:taskfile path=Taskfile.yml")
            a(taskfile_path.read_text(encoding="utf-8").rstrip())
            a("```")
            a("")
    else:
        a("```yaml markpact:taskfile path=Taskfile.yml")
        a("tasks:")
        for t in tasks:
            a(f"  {t['name']}:")
            if t["desc"]:
                a(f'    desc: "{t["desc"]}"')
            if t["cmd"]:
                a("    cmds:")
                a(f"      - {t['cmd']}")
        a("```")
        a("")


def _render_workflows(
    doql: dict, tasks: list, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Workflows")
    a("")
    if doql.get("workflows") and not raw_sources:
        _render_workflows_doql(doql, L)
    if tasks:
        _render_workflows_taskfile(tasks, proj_dir, raw_sources, L)
    return L


def _render_quality_raw(proj_dir: Path, L: list[str]) -> None:
    a = L.append
    pyqual_path = proj_dir / "pyqual.yaml"
    if pyqual_path.exists():
        a("```yaml markpact:pyqual path=pyqual.yaml")
        a(pyqual_path.read_text(encoding="utf-8").rstrip())
        a("```")
        a("")


def _render_quality_parsed(pyqual: dict, L: list[str]) -> None:
    a = L.append
    if pyqual.get("name"):
        a(f"**Pipeline**: `{pyqual['name']}`")
        a("")
    if pyqual.get("metrics"):
        a("### Metrics / Thresholds")
        a("")
        for k, v in pyqual["metrics"].items():
            a(f"- `{k}`: `{v}`")
        a("")
    if pyqual.get("stages"):
        a("### Stages")
        a("")
        for s in pyqual["stages"]:
            opt = " *(optional)*" if s.get("optional") else ""
            a(f"- **{s['name']}**: `{s['tool']}`{opt}")
        a("")
    if pyqual.get("loop"):
        a("### Loop Behavior")
        a("")
        for k, v in pyqual["loop"].items():
            a(f"- `{k}`: `{v}`")
        a("")


def _render_quality(pyqual: dict, proj_dir: Path, raw_sources: bool) -> list[str]:
    if not pyqual:
        return []
    L: list[str] = []
    a = L.append
    a("## Quality Pipeline (`pyqual.yaml`)")
    a("")
    if raw_sources:
        _render_quality_raw(proj_dir, L)
    else:
        _render_quality_parsed(pyqual, L)
    return L


def _render_deps_runtime(deps: list, node_deps: list, L: list[str]) -> None:
    a = L.append
    if deps:
        a("### Runtime")
        a("")
        a("```text markpact:deps python")
        for dep in deps:
            a(dep)
        a("```")
        a("")
    elif node_deps:
        a("### Runtime (Node.js)")
        a("")
        a("```text markpact:deps node")
        for dep in node_deps[:30]:
            a(dep)
        if len(node_deps) > 30:
            a(f"# (+{len(node_deps) - 30} more)")
        a("```")
        a("")
    else:
        a("### Runtime")
        a("")
        a("*(see pyproject.toml)*")
        a("")


def _render_deps_dev(dev_deps: list, node_dev: list, L: list[str]) -> None:
    a = L.append
    if dev_deps:
        a("### Development")
        a("")
        a("```text markpact:deps python scope=dev")
        for dep in dev_deps:
            a(dep)
        a("```")
        a("")
    elif node_dev:
        a("### Development (Node.js)")
        a("")
        a("```text markpact:deps node scope=dev")
        for dep in node_dev[:20]:
            a(dep)
        if len(node_dev) > 20:
            a(f"# (+{len(node_dev) - 20} more)")
        a("```")
        a("")


def _render_dependencies(
    deps: list, dev_deps: list, pkg_json: dict | None = None
) -> list[str]:
    pkg_json = pkg_json or {}
    L: list[str] = []
    a = L.append
    a("## Dependencies")
    a("")
    _render_deps_runtime(deps, pkg_json.get("dependencies", []), L)
    _render_deps_dev(dev_deps, pkg_json.get("devDependencies", []), L)
    return L


def _render_deployment_install(pkg_json: dict, name: str, L: list[str]) -> None:
    a = L.append
    if pkg_json.get("name"):
        a("```bash markpact:run")
        a(f"npm install {pkg_json['name']}")
        a("```")
    else:
        a("```bash markpact:run")
        a(f"pip install {name}")
        a("")
        a("# development install")
        a("pip install -e .[dev]")
        a("```")
    a("")


def _render_deployment_reqs(reqs: list, L: list[str]) -> None:
    if not reqs:
        return
    a = L.append
    a("### Requirements Files")
    a("")
    for r in reqs:
        a(f"#### `{r['file']}`")
        a("")
        for dep in r["deps"][:20]:
            a(f"- `{dep}`")
        if len(r["deps"]) > 20:
            a(f"- *(+{len(r['deps']) - 20} more)*")
        a("")


def _render_deployment_docker(dockerfile: dict, compose: dict, L: list[str]) -> None:
    a = L.append
    if dockerfile:
        a("### Docker")
        a("")
        a(f"- **base image**: `{dockerfile['from']}`")
        if dockerfile["ports"]:
            a(f"- **expose**: {', '.join(f'`{p}`' for p in dockerfile['ports'])}")
        if dockerfile["entrypoint"]:
            a(f"- **entrypoint**: `{dockerfile['entrypoint']}`")
        if dockerfile["labels"]:
            for k, v in dockerfile["labels"].items():
                a(f"- **label** `{k}`: {v}")
        a("")
    if compose.get("services"):
        a(f"### Docker Compose (`{compose['file']}`)")
        a("")
        for svc in compose["services"]:
            ports_str = (
                ", ".join(f"`{p}`" for p in svc["ports"]) if svc["ports"] else ""
            )
            image_str = f" image=`{svc['image']}`" if svc["image"] else ""
            a(
                f"- **{svc['name']}**{image_str}"
                + (f" ports: {ports_str}" if ports_str else "")
            )
        a("")


def _render_deployment(
    pkg_json: dict, name: str, reqs: list, dockerfile: dict, compose: dict
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Deployment")
    a("")
    _render_deployment_install(pkg_json, name, L)
    _render_deployment_reqs(reqs, L)
    _render_deployment_docker(dockerfile, compose, L)
    return L


def _render_extras(makefile: list, pkg_json: dict) -> list[str]:
    L: list[str] = []
    a = L.append
    if makefile:
        a("## Makefile Targets")
        a("")
        for t in makefile:
            desc = f" — {t['desc']}" if t["desc"] else ""
            a(f"- `{t['target']}`{desc}")
        a("")
    if pkg_json.get("scripts"):
        a("## Node.js Scripts (`package.json`)")
        a("")
        if pkg_json.get("description"):
            a(pkg_json["description"])
            a("")
        for script, cmd in pkg_json["scripts"].items():
            a(f"- `npm run {script}` — `{cmd}`")
        a("")
        if pkg_json.get("dependencies"):
            a(
                "**Runtime deps**: "
                + ", ".join(f"`{d}`" for d in pkg_json["dependencies"][:15])
            )
            a("")
        if pkg_json.get("engines"):
            for eng, ver in pkg_json["engines"].items():
                a(f"- **{eng}**: `{ver}`")
            a("")
    return L


def _render_code_analysis(
    project_analysis: list, skip_files: set[str] | None = None
) -> list[str]:
    """Render Code Analysis section, optionally skipping files handled by other sections."""
    skip_files = skip_files or set()
    entries = [
        e
        for e in project_analysis
        if not any(s in e.get("file", "") for s in skip_files)
    ]
    if not entries:
        return []
    L: list[str] = []
    a = L.append
    a("## Code Analysis")
    a("")
    for entry in entries:
        a(f"### `{entry['file']}`")
        a("")
        lang = entry["lang"]
        if lang == "markdown":
            a(entry["content"])
        elif lang == "text":
            a(f"```text markpact:analysis path={entry['file']}")
            a(entry["content"])
            a("```")
        else:
            a(f"```{lang} markpact:analysis path={entry['file']}")
            a(entry["content"])
            a("```")
        a("")
    return L


def _render_source_snippets(source_snippets: list, top_n: int = 5) -> list[str]:
    """Render top-N modules with function/class signatures for LLM orientation."""
    if not source_snippets:
        return []
    L: list[str] = []
    a = L.append
    a("## Source Map")
    a("")
    a(
        f"*Top {min(top_n, len(source_snippets))} modules by symbol density — signatures for LLM orientation.*"
    )
    a("")
    for entry in source_snippets[:top_n]:
        a(f"### `{entry['module']}` (`{entry['path']}`)")
        a("")
        a("```python")
        for fn in entry["funcs"]:
            args_str = ", ".join(fn["args"])
            cc_flag = " ⚠" if fn["cc"] >= 10 else ""
            a(
                f"def {fn['name']}({args_str})  # CC={fn['cc']}, fan={fn['fan']}{cc_flag}"
            )
        for cls in entry["classes"]:
            doc = cls["doc"]  # already formatted as "  # ..." or ""
            a(f"class {cls['name']}:{doc}")
            for m in cls["methods"]:
                args_str = ", ".join(m["args"])
                cc_flag = " ⚠" if m["cc"] >= 10 else ""
                a(f"    def {m['name']}({args_str})  # CC={m['cc']}{cc_flag}")
        a("```")
        a("")
    return L


def _render_api_stubs(openapi: dict) -> list[str]:
    """Render OpenAPI endpoints as Python-like typed stubs for LLM orientation."""
    endpoints = openapi.get("endpoints", [])
    schemas = openapi.get("schemas", [])
    if not endpoints:
        return []
    L: list[str] = []
    a = L.append
    a("## API Stubs")
    a("")
    title = openapi.get("title", "")
    version = openapi.get("version", "")
    if title:
        a(f"*{title} v{version} — auto-generated stubs from `openapi.yaml`.*")
        a("")

    # Group by tag for structure
    by_tag: dict[str, list[dict]] = {}
    for ep in endpoints:
        tag = ep["tags"][0] if ep.get("tags") else "default"
        by_tag.setdefault(tag, []).append(ep)

    a("```python markpact:openapi path=openapi.yaml")
    for tag, eps in by_tag.items():
        a(f"# {tag}")
        for ep in eps:
            op_id = (
                ep.get("operationId")
                or f"{ep['method'].lower()}_{ep['path'].replace('/', '_').strip('_')}"
            )
            summary = f"  # {ep['summary']}" if ep.get("summary") else ""
            a(f"def {op_id}() -> Response:{summary}")
            a(f'    "{ep["method"]} {ep["path"]}"')
        a("")
    a("```")
    a("")
    if schemas:
        a("**Schemas**: " + ", ".join(f"`{s}`" for s in schemas))
        a("")
    return L


def _render_test_contracts(scenarios: list) -> list[str]:
    """Render test scenarios as contract signatures — endpoint + key assertions."""
    if not scenarios:
        return []
    L: list[str] = []
    a = L.append
    a("## Test Contracts")
    a("")
    a("*Scenarios as contract signatures — what the system guarantees.*")
    a("")

    # Group by type
    by_type: dict[str, list[dict]] = {}
    for sc in scenarios:
        sc_type = sc.get("type", "unknown")
        by_type.setdefault(sc_type, []).append(sc)

    for sc_type, scs in sorted(by_type.items()):
        a(f"### {sc_type.title()} ({len(scs)})")
        a("")
        for sc in scs:
            a(f"**`{sc['name']}`**")
            if sc.get("endpoints"):
                for ep in sc["endpoints"][:3]:
                    status = ep.get("status", "")
                    op = f" — `{ep['operationId']}`" if ep.get("operationId") else ""
                    a(f"- `{ep['method']} {ep['path']}` → `{status}`{op}")
            if sc.get("asserts"):
                for ass in sc["asserts"][:3]:
                    a(f"- assert `{ass['field']} {ass['op']} {ass['expected']}`")
            if sc.get("performance"):
                for p in sc["performance"][:2]:
                    a(f"- perf `{p['metric']} < {p['threshold']}`")
            if sc.get("detectors"):
                a(f"- detectors: {sc['detectors']}")
            a("")
    return L


def _parse_calls_header(lines: list[str]) -> dict:
    """Parse node/edge/module counts and CC average from header comments."""
    result = {"nodes": 0, "edges": 0, "modules_count": 0, "cc_avg": 0.0}
    for line in lines[:5]:
        if line.startswith("# nodes:"):
            m = re.search(
                r"nodes:\s*(\d+).*edges:\s*(\d+).*modules:\s*(\d+)", line
            )
            if m:
                result["nodes"] = int(m.group(1))
                result["edges"] = int(m.group(2))
                result["modules_count"] = int(m.group(3))
        if line.startswith("# CC"):
            m = re.search(r"CC[̄=\u0304]=?\s*([\d.]+)", line)
            if m:
                result["cc_avg"] = float(m.group(1))
    return result


def _parse_calls_hubs(lines: list[str]) -> list[dict]:
    """Parse HUBS section into list of hub dicts."""
    hubs: list[dict] = []
    in_hubs = False
    current_hub: dict = {}
    for line in lines:
        if line.startswith("HUBS["):
            in_hubs = True
            continue
        if in_hubs and line and not line.startswith(" "):
            in_hubs = False
        if in_hubs and line.startswith("  ") and not line.startswith("    "):
            if current_hub:
                hubs.append(current_hub)
            current_hub = {"name": line.strip()}
        elif in_hubs and line.startswith("    "):
            m = re.search(r"CC=(\d+)\s+in:(\d+)\s+out:(\d+)\s+total:(\d+)", line)
            if m and current_hub:
                current_hub.update(
                    {
                        "cc": int(m.group(1)),
                        "in": int(m.group(2)),
                        "out": int(m.group(3)),
                        "total": int(m.group(4)),
                    }
                )
    if current_hub:
        hubs.append(current_hub)
    return hubs


def _parse_calls_toon(content: str) -> dict:
    """Parse calls.toon.yaml text into structured dict for rendering."""
    lines = content.splitlines()
    return {
        **_parse_calls_header(lines),
        "hubs": _parse_calls_hubs(lines),
        "modules": [],
    }


def _render_call_graph(project_analysis: list) -> list[str]:
    """Render call graph summary from calls.toon.yaml in project_analysis."""
    calls_entry = next(
        (e for e in project_analysis if "calls.toon" in e.get("file", "")), None
    )
    if not calls_entry:
        return []

    data = _parse_calls_toon(calls_entry["content"])
    if not data["hubs"]:
        return []

    L: list[str] = []
    a = L.append
    a("## Call Graph")
    a("")
    a(
        f"*{data['nodes']} nodes · {data['edges']} edges · {data['modules_count']} modules · CC̄={data['cc_avg']}*"
    )
    a("")

    # Top hubs table (top 8 by total degree)
    top_hubs = sorted(data["hubs"], key=lambda h: h.get("total", 0), reverse=True)[:8]
    a("### Hubs (by degree)")
    a("")
    a("| Function | CC | in | out | total |")
    a("|----------|----|----|-----|-------|")
    for hub in top_hubs:
        name = hub["name"].split(".")[-1]  # short name
        module = ".".join(hub["name"].split(".")[:-1])
        cc_flag = " ⚠" if hub.get("cc", 0) >= 10 else ""
        a(
            f"| `{name}` *(in {module})* | {hub.get('cc', 0)}{cc_flag} | {hub.get('in', 0)} | {hub.get('out', 0)} | **{hub.get('total', 0)}** |"
        )
    a("")

    # Full embed for LLM reference under markpact tag
    rel = calls_entry["file"]
    a(f"```toon markpact:analysis path={rel}")
    a(calls_entry["content"].rstrip())
    a("```")
    a("")
    return L


# ---------------------------------------------------------------------------
# Main renderer helpers
# ---------------------------------------------------------------------------


def _collect_pkg_sources(
    pyproj: dict,
    reqs: list,
    tasks: list,
    makefile: list,
    scenarios: list,
    openapi: dict,
    doql: dict,
    pyqual: dict,
    goal: dict,
    env_vars: list,
) -> list[str]:
    """Collect source labels for code/pipeline sources."""
    sources: list[str] = []
    if pyproj:
        sources.append("pyproject.toml")
    if reqs:
        sources.extend(r["file"] for r in reqs)
    if tasks:
        sources.append("Taskfile.yml")
    if makefile:
        sources.append("Makefile")
    if scenarios:
        sources.append(f"testql({len(scenarios)})")
    if openapi.get("endpoints"):
        sources.append(f"openapi({len(openapi['endpoints'])} ep)")
    if doql.get("app") or doql.get("workflows") or doql.get("entities"):
        sources.extend(doql.get("sources", ["app.doql.less"]))
    if pyqual.get("stages"):
        sources.append("pyqual.yaml")
    if goal.get("name"):
        sources.append("goal.yaml")
    if env_vars:
        sources.append(".env.example")
    return sources


def _collect_infra_sources(
    dockerfile: dict,
    compose: dict,
    pkg_json: dict,
    modules: list,
    project_analysis: list,
) -> list[str]:
    """Collect source labels for infra/module sources."""
    sources: list[str] = []
    if dockerfile:
        sources.append("Dockerfile")
    if compose.get("services"):
        sources.append(compose.get("file", "docker-compose.yml"))
    if pkg_json.get("name"):
        sources.append("package.json")
    if modules:
        sources.append(f"src({len(modules)} mod)")
    if project_analysis:
        sources.append(f"project/({len(project_analysis)} analysis files)")
    return sources


def _collect_sources(
    pyproj: dict,
    reqs: list,
    tasks: list,
    makefile: list,
    scenarios: list,
    openapi: dict,
    doql: dict,
    pyqual: dict,
    goal: dict,
    env_vars: list,
    dockerfile: dict,
    compose: dict,
    pkg_json: dict,
    modules: list,
    project_analysis: list,
) -> list[str]:
    """Build the list of source labels that contributed data to this SUMD."""
    return _collect_pkg_sources(
        pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars
    ) + _collect_infra_sources(dockerfile, compose, pkg_json, modules, project_analysis)


def _render_metadata_section(
    name: str,
    version: str,
    py_req: str,
    license_: str,
    ai_model: str,
    openapi: dict,
    sources_used: list[str],
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Metadata")
    a("")
    a(f"- **name**: `{name}`")
    a(f"- **version**: `{version}`")
    if py_req:
        a(f"- **python_requires**: `{py_req}`")
    if license_:
        a(f"- **license**: {license_}")
    if ai_model:
        a(f"- **ai_model**: `{ai_model}`")
    a("- **ecosystem**: SUMD + DOQL + testql + taskfile")
    if openapi.get("title"):
        a(f"- **openapi_title**: {openapi['title']} v{openapi.get('version', '')}")
    a(f"- **generated_from**: {', '.join(sources_used)}")
    a("")
    return L


def _render_configuration_section(name: str, version: str) -> list[str]:
    return [
        "## Configuration",
        "",
        "```yaml",
        "project:",
        f"  name: {name}",
        f"  version: {version}",
        "  env: local",
        "```",
        "",
    ]


def _render_env_section(env_vars: list) -> list[str]:
    if not env_vars:
        return []
    L: list[str] = []
    a = L.append
    a("## Environment Variables (`.env.example`)")
    a("")
    a("| Variable | Default | Description |")
    a("|----------|---------|-------------|")
    for v in env_vars:
        desc = v["comment"].replace("|", "\\|")
        a(f"| `{v['key']}` | `{v['default']}` | {desc} |")
    a("")
    return L


def _render_goal_section(goal: dict) -> list[str]:
    if not goal.get("name"):
        return []
    L: list[str] = []
    a = L.append
    a("## Release Management (`goal.yaml`)")
    a("")
    if goal.get("versioning_strategy"):
        a(f"- **versioning**: `{goal['versioning_strategy']}`")
    if goal.get("commit_strategy"):
        a(
            f"- **commits**: `{goal['commit_strategy']}` scope=`{goal.get('commit_scope', '')}`"
        )
    if goal.get("changelog_template"):
        a(f"- **changelog**: `{goal['changelog_template']}`")
    if goal.get("strategies"):
        a(f"- **build strategies**: {', '.join(f'`{s}`' for s in goal['strategies'])}")
    if goal.get("version_files"):
        a(f"- **version files**: {', '.join(f'`{f}`' for f in goal['version_files'])}")
    a("")
    return L


def _inject_toc(content: str) -> str:
    """Inject a ## Contents TOC block before ## Metadata."""
    h2_sections = re.findall(r"^## (.+)$", content, re.MULTILINE)
    if not h2_sections:
        return content
    toc_lines = ["## Contents", ""]
    for sec in h2_sections:
        anchor = re.sub(r"[^\w\s-]", "", sec.lower()).strip()
        anchor = re.sub(r"\s+", "-", anchor)
        toc_lines.append(f"- [{sec}](#{anchor})")
    toc_lines.append("")
    toc_block = "\n".join(toc_lines)
    return re.sub(
        r"(\n## Metadata\n)", f"\n{toc_block}\n## Metadata\n", content, count=1
    )


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------


def generate_sumd_content(
    proj_dir: Path,
    return_sources: bool = False,
    raw_sources: bool = True,
    profile: str = "rich",
) -> str | tuple[str, list[str]]:
    """Generate SUMD.md content from a project directory.

    Delegates to RenderPipeline — kept for backwards compatibility.
    """
    from sumd.pipeline import RenderPipeline  # local import to avoid circular

    return RenderPipeline(proj_dir, raw_sources=raw_sources).run(
        profile=profile, return_sources=return_sources
    )
