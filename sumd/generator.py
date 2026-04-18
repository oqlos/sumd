"""SUMD Generator — extract metadata from project source files and render SUMD.md.

Sources read per project:
  pyproject.toml          → name, version, description, dependencies, scripts, python_requires
  Taskfile.yml            → tasks with descriptions and commands        (taskfile layer)
  testql-scenarios/*.yaml → scenario names, types, endpoints, asserts   (testql layer)
  openapi.yaml            → full REST API surface with operationIds      (openapi layer)
  app.doql.less           → DOQL app block, interfaces, integrations, workflows  (doql layer)
  pyqual.yaml             → quality pipeline stages and metrics
  <pkg>/*.py              → Python source modules
  README.md               → project title
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def _read_toml(path: Path) -> dict:
    try:
        import tomllib
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except ImportError:
        import toml
        return toml.loads(path.read_text(encoding="utf-8"))


def extract_pyproject(proj_dir: Path) -> dict[str, Any]:
    toml_path = proj_dir / "pyproject.toml"
    if not toml_path.exists():
        return {}
    try:
        data = _read_toml(toml_path)
        project = data.get("project", {})
        optional = project.get("optional-dependencies", {})
        dev_deps = optional.get("dev", [])
        pfix = data.get("tool", {}).get("pfix", {})
        return {
            "name": project.get("name", proj_dir.name),
            "version": project.get("version", "0.0.0"),
            "description": project.get("description", ""),
            "python_requires": project.get("requires-python", ""),
            "license": project.get("license", ""),
            "dependencies": project.get("dependencies", []),
            "dev_dependencies": dev_deps,
            "scripts": list(project.get("scripts", {}).keys()),
            "ai_model": pfix.get("model", ""),
        }
    except Exception:
        return {}


def extract_taskfile(proj_dir: Path) -> list[dict[str, str]]:
    taskfile_path = proj_dir / "Taskfile.yml"
    if not taskfile_path.exists():
        return []
    try:
        data = yaml.safe_load(taskfile_path.read_text(encoding="utf-8"))
        tasks = data.get("tasks", {}) or {}
        result = []
        for task_name, body in tasks.items():
            if not isinstance(body, dict):
                continue
            desc = body.get("desc", "")
            cmds = body.get("cmds", [])
            first_cmd = ""
            for c in cmds:
                if isinstance(c, str):
                    first_cmd = c.strip()
                    break
                elif isinstance(c, dict) and "cmd" in c:
                    first_cmd = c["cmd"].strip()
                    break
            result.append({"name": task_name, "desc": desc, "cmd": first_cmd})
        return result
    except Exception:
        return []


def _parse_toon_file(f: Path) -> dict[str, Any]:
    """Parse a single *.testql.toon.yaml file into a scenario dict."""
    content = f.read_text(encoding="utf-8")

    def _match(pattern: str) -> str:
        m = re.search(pattern, content, re.MULTILINE)
        return m.group(1).strip() if m else ""

    # CONFIG block: key, value pairs (skip detected_* and variable-reference rows)
    config: dict[str, str] = {}
    in_config = False
    for line in content.splitlines():
        if re.match(r"^CONFIG\[\d+\]", line):
            in_config = True
            continue
        if in_config:
            if re.match(r"^[A-Z_]+\[\d+\]", line) or line.startswith("#"):
                in_config = False
            elif m := re.match(r"^\s{2}([a-z_]+),\s*(.+)$", line):
                k, v = m.group(1), m.group(2).strip()
                if not k.startswith("detected") and "${" not in v:
                    config[k] = v

    # API endpoints: GET/POST/... , /path, status  [# op_id - summary | # summary]
    api_rows = re.findall(
        r"^\s+(GET|POST|PUT|DELETE|PATCH),\s+(/[^\s,]+),\s+(\d+)"
        r"(?:\s+#\s*(\S+)\s+-\s*(.+)|\s+#\s*(.+))?",
        content, re.MULTILINE,
    )
    endpoints: list[dict[str, Any]] = []
    for method, path, status, op_id, summary_a, summary_b in api_rows:
        ep: dict[str, Any] = {"method": method, "path": path, "status": int(status)}
        if op_id:
            ep["operationId"] = op_id
        summary = (summary_a or summary_b or "").strip()
        if summary:
            ep["summary"] = summary
        endpoints.append(ep)

    # ASSERT block: field, operator, expected
    assert_rows: list[dict[str, str]] = []
    in_assert = False
    for line in content.splitlines():
        if re.match(r"^ASSERT\[\d+\]", line):
            in_assert = True
            continue
        if in_assert:
            if re.match(r"^[A-Z_]+\[\d+\]", line) or line.startswith("#"):
                in_assert = False
            elif m := re.match(r"^\s{2}([a-z_]+),\s*([<>=!]+),\s*(.+)$", line):
                assert_rows.append({"field": m.group(1), "op": m.group(2), "expected": m.group(3).strip()})

    # PERFORMANCE block: metric, threshold
    perf: list[dict[str, str]] = []
    in_perf = False
    for line in content.splitlines():
        if re.match(r"^PERFORMANCE\[\d+\]", line):
            in_perf = True
            continue
        if in_perf:
            if re.match(r"^[A-Z_]+\[\d+\]", line) or line.startswith("#"):
                in_perf = False
            elif m := re.match(r"^\s{2}([a-z_]+),\s*(.+)$", line):
                perf.append({"metric": m.group(1), "threshold": m.group(2).strip()})

    # NAVIGATE block: url rows
    navigate_urls: list[str] = []
    in_nav = False
    for line in content.splitlines():
        if re.match(r"^NAVIGATE\[\d+\]", line):
            in_nav = True
            continue
        if in_nav:
            if re.match(r"^[A-Z_]+\[\d+\]", line) or line.startswith("#"):
                in_nav = False
            elif stripped := line.strip():
                navigate_urls.append(stripped)

    # GUI block: action, selector rows
    gui_actions: list[dict[str, str]] = []
    in_gui = False
    for line in content.splitlines():
        if re.match(r"^GUI\[\d+\]", line):
            in_gui = True
            continue
        if in_gui:
            if re.match(r"^[A-Z_]+\[\d+\]", line) or line.startswith("#"):
                in_gui = False
            elif m := re.match(r"^\s{2}(\w+),\s*(.+)$", line):
                gui_actions.append({"action": m.group(1), "selector": m.group(2).strip()})

    return {
        "file": f.name,
        "rel_path": str(f),
        "name": _match(r"^#\s*SCENARIO:\s*(.+)") or f.stem,
        "type": _match(r"^#\s*TYPE:\s*(\S+)") or "unknown",
        "generated": _match(r"^#\s*GENERATED:\s*(\S+)") or "false",
        "detectors": _match(r"^#\s*DETECTORS:\s*(.+)"),
        "config": config,
        "endpoints": endpoints,
        "asserts": assert_rows,
        "performance": perf,
        "navigate": navigate_urls,
        "gui": gui_actions,
    }


def extract_testql_scenarios(proj_dir: Path) -> list[dict[str, Any]]:
    """Scan all *.testql.toon.yaml and testql-scenarios/*.yaml files in project."""
    collected: dict[str, Path] = {}  # stem -> path, dedup by stem

    # 1. testql-scenarios/ directory (any *.yaml)
    for f in sorted((proj_dir / "testql-scenarios").glob("*.yaml")):
        collected[f.name] = f

    # 2. root-level *.testql.toon.yaml files
    for f in sorted(proj_dir.glob("*.testql.toon.yaml")):
        collected[f.name] = f

    # 3. nested <pkg>/scenarios/**/*.testql.toon.yaml
    pkg_dir = proj_dir / proj_dir.name
    for f in sorted(pkg_dir.rglob("*.testql.toon.yaml")):
        collected[f.name] = f

    scenarios = []
    for f in sorted(collected.values(), key=lambda p: p.name):
        try:
            sc = _parse_toon_file(f)
        except Exception:
            continue
        # Store relative path for display (relative to proj_dir)
        try:
            sc["rel_path"] = str(f.relative_to(proj_dir))
        except ValueError:
            sc["rel_path"] = f.name
        scenarios.append(sc)

    return scenarios


def extract_openapi(proj_dir: Path) -> dict[str, Any]:
    openapi_path = proj_dir / "openapi.yaml"
    if not openapi_path.exists():
        return {}
    try:
        data = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
        info = data.get("info", {})
        paths = data.get("paths", {}) or {}
        endpoints = []
        seen: set[tuple] = set()
        for path, methods in paths.items():
            if not isinstance(methods, dict) or "://" in path:
                continue
            for method, spec in methods.items():
                if method not in ("get", "post", "put", "delete", "patch"):
                    continue
                if not isinstance(spec, dict):
                    continue
                key = (method.upper(), path)
                if key in seen:
                    continue
                seen.add(key)
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "operationId": spec.get("operationId", ""),
                    "summary": spec.get("summary", ""),
                    "tags": spec.get("tags", []),
                })
        schemas = list((data.get("components", {}) or {}).get("schemas", {}).keys())
        return {
            "title": info.get("title", ""),
            "version": info.get("version", ""),
            "description": info.get("description", ""),
            "endpoints": endpoints,
            "schemas": schemas,
        }
    except Exception:
        return {}


def _parse_doql_content(content: str) -> dict[str, Any]:
    """Parse DOQL content from .less or .css file into structured data."""
    app_block = re.search(r"app\s*\{([^}]+)\}", content, re.DOTALL)
    app_meta: dict[str, str] = {}
    if app_block:
        for line in app_block.group(1).splitlines():
            m = re.match(r"\s*(\w+):\s*(.+?);", line)
            if m:
                app_meta[m.group(1)] = m.group(2).strip()

    entities: list[dict[str, Any]] = []
    for m in re.finditer(
        r'entity\[name="([^"]+)"\](?:\s*page\[name="([^"]+)"\])?\s*\{([^}]*)\}',
        content, re.DOTALL,
    ):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(3)))
        entry: dict[str, Any] = {"name": m.group(1)}
        if m.group(2):
            entry["page"] = m.group(2)
        if attrs:
            entry["attrs"] = attrs
        entities.append(entry)

    interfaces: list[dict[str, Any]] = []
    for m in re.finditer(
        r'interface\[([^\]]+)\](?:\s*page\[name="([^"]+)"\])?\s*\{([^}]*)\}',
        content, re.DOTALL,
    ):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(3)))
        entry: dict[str, Any] = {"selector": m.group(1).strip()}
        if m.group(2):
            entry["page"] = m.group(2)
        entry.update(attrs)
        interfaces.append(entry)

    integrations: list[dict[str, Any]] = []
    for m in re.finditer(r'integration\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(2)))
        integrations.append({"selector": m.group(1).strip(), **attrs})

    workflows: list[dict[str, Any]] = []
    for m in re.finditer(r'workflow\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        name_m = re.search(r'name="([^"]+)"', m.group(1))
        steps = re.findall(r'step-\d+:\s*run cmd=(.+?);', m.group(2))
        trigger_m = re.search(r'trigger:\s*(\S+?);', m.group(2))
        workflows.append({
            "name": name_m.group(1) if name_m else m.group(1).strip(),
            "trigger": trigger_m.group(1) if trigger_m else "manual",
            "steps": [s.strip() for s in steps],
        })

    return {
        "app": app_meta,
        "entities": entities,
        "interfaces": interfaces,
        "integrations": integrations,
        "workflows": workflows,
    }


def extract_doql(proj_dir: Path) -> dict[str, Any]:
    """Read app.doql.less and/or app.doql.css and merge into one dict."""
    combined = ""
    sources_found: list[str] = []
    for fname in ("app.doql.less", "app.doql.css"):
        p = proj_dir / fname
        if p.exists():
            combined += p.read_text(encoding="utf-8") + "\n"
            sources_found.append(fname)
    if not sources_found:
        return {}
    result = _parse_doql_content(combined)
    result["sources"] = sources_found
    return result


def extract_pyqual(proj_dir: Path) -> dict[str, Any]:
    pyqual_path = proj_dir / "pyqual.yaml"
    if not pyqual_path.exists():
        return {}
    try:
        data = yaml.safe_load(pyqual_path.read_text(encoding="utf-8"))
        pipeline = data.get("pipeline", data)
        metrics = pipeline.get("metrics", {})
        stages = [
            {
                "name": s["name"],
                "tool": s.get("tool", s.get("run", "")),
                "optional": s.get("optional", False),
            }
            for s in pipeline.get("stages", [])
            if isinstance(s, dict)
        ]
        return {
            "name": pipeline.get("name", ""),
            "metrics": metrics,
            "stages": stages,
            "loop": pipeline.get("loop", {}),
        }
    except Exception:
        return {}


def extract_python_modules(proj_dir: Path, pkg_name: str) -> list[str]:
    pkg_dir = proj_dir / pkg_name
    if not pkg_dir.exists():
        return []
    return [p.stem for p in sorted(pkg_dir.glob("*.py")) if not p.stem.startswith("__")]


def extract_readme_title(proj_dir: Path) -> str:
    readme = proj_dir / "README.md"
    if not readme.exists():
        return ""
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def generate_sumd_content(  # noqa: C901
    proj_dir: Path,
    return_sources: bool = False,
) -> str | tuple[str, list[str]]:
    """Generate SUMD.md content from a project directory.

    Args:
        proj_dir: Path to the project root.
        return_sources: If True, return (content, sources_list) instead of just content.

    Returns:
        Rendered SUMD.md string, or (string, list[str]) when return_sources=True.
    """
    pkg_name = proj_dir.name
    sources_used: list[str] = []

    pyproj   = extract_pyproject(proj_dir)
    tasks    = extract_taskfile(proj_dir)
    scenarios = extract_testql_scenarios(proj_dir)
    openapi  = extract_openapi(proj_dir)
    doql     = extract_doql(proj_dir)
    pyqual   = extract_pyqual(proj_dir)
    modules  = extract_python_modules(proj_dir, pkg_name)
    title    = extract_readme_title(proj_dir)

    # Track which source files contributed data
    if pyproj:
        sources_used.append("pyproject.toml")
    if tasks:
        sources_used.append("Taskfile.yml")
    if scenarios:
        sources_used.append(f"testql({len(scenarios)})")
    if openapi.get("endpoints"):
        sources_used.append(f"openapi({len(openapi['endpoints'])} ep)")
    if doql.get("app") or doql.get("workflows") or doql.get("entities"):
        sources_used.extend(doql.get("sources", ["app.doql.less"]))
    if pyqual.get("stages"):
        sources_used.append("pyqual.yaml")
    if modules:
        sources_used.append(f"src({len(modules)} mod)")

    name        = pyproj.get("name", pkg_name)
    version     = pyproj.get("version", "0.0.0")
    description = pyproj.get("description", title or name)
    py_req      = pyproj.get("python_requires", "")
    license_    = pyproj.get("license", "")
    deps        = pyproj.get("dependencies", [])
    dev_deps    = pyproj.get("dev_dependencies", [])
    scripts     = pyproj.get("scripts", [])
    ai_model    = pyproj.get("ai_model", "")

    L: list[str] = []
    a = L.append

    # ── Title ────────────────────────────────────────────────────────────
    a(f"# {title or name}")
    a("")
    a(description)
    a("")

    # ── Metadata ─────────────────────────────────────────────────────────
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
    a(f"- **ecosystem**: SUMD + DOQL + testql + taskfile")
    if openapi.get("title"):
        a(f"- **openapi_title**: {openapi['title']} v{openapi.get('version', '')}")
    a(f"- **generated_from**: {', '.join(sources_used)}")
    a("")

    # ── Intent ───────────────────────────────────────────────────────────
    a("## Intent")
    a("")
    a(description)
    a("")

    # ── Architecture ─────────────────────────────────────────────────────
    a("## Architecture")
    a("")
    a("```")
    a("SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)")
    a("```")
    a("")

    if doql.get("app") or doql.get("entities") or doql.get("interfaces"):
        doql_sources = ", ".join(f"`{s}`" for s in doql.get("sources", ["app.doql.less"]))
        a(f"### DOQL Application Declaration ({doql_sources})")
        a("")
        if doql.get("app"):
            a("```less")
            a("app {")
            for k, v in doql["app"].items():
                a(f"  {k}: {v};")
            a("}")
            a("```")
            a("")

    if doql.get("entities"):
        a("### DOQL Data Model (`entity`)")
        a("")
        for ent in doql["entities"]:
            attrs_str = ""
            if ent.get("attrs"):
                attrs_str = " — " + ", ".join(f"`{k}: {v}`" for k, v in ent["attrs"].items())
            page_str = f" page=`{ent['page']}`" if ent.get("page") else ""
            a(f"- `entity[{ent['name']}]`{page_str}{attrs_str}")
        a("")

    if doql.get("interfaces"):
        a("### DOQL Interfaces")
        a("")
        for iface in list(doql["interfaces"]):
            sel = iface.get("selector", "")
            attrs = ", ".join(f"{k}: {v}" for k, v in iface.items() if k not in ("selector", "page"))
            page_str = f" page=`{iface['page']}`" if iface.get("page") else ""
            a(f"- `interface[{sel}]`{page_str} — {attrs}")
        a("")

    if doql.get("integrations"):
        a("### DOQL Integrations")
        a("")
        for intg in list(doql["integrations"]):
            sel = intg.get("selector", "")
            attrs = ", ".join(f"{k}: {v}" for k, v in intg.items() if k != "selector")
            a(f"- `integration[{sel}]` — {attrs}")
        a("")

    if modules:
        a("### Source Modules")
        a("")
        for mod in modules:
            a(f"- `{name}.{mod}`")
        a("")

    # ── Interfaces ───────────────────────────────────────────────────────
    a("## Interfaces")
    a("")

    if scripts:
        a("### CLI Entry Points")
        a("")
        for s in scripts:
            a(f"- `{s}`")
        a("")

    if openapi.get("endpoints"):
        a("### REST API (from `openapi.yaml`)")
        a("")
        a("| Method | Path | OperationId | Summary |")
        a("|--------|------|-------------|---------|")
        for ep in openapi["endpoints"]:
            summary = ep.get("summary", "").replace("|", "\\|")
            a(f"| `{ep['method']}` | `{ep['path']}` | `{ep['operationId']}` | {summary} |")
        a("")
        if openapi.get("schemas"):
            a("**Schemas**: " + ", ".join(f"`{s}`" for s in openapi["schemas"]))
            a("")

    if scenarios:
        a("### testql Scenarios")
        a("")
        for sc in scenarios:
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
                    op = f" — `{ep['operationId']}`" if ep.get("operationId") else ""
                    sm = f": {ep['summary']}" if ep.get("summary") else ""
                    a(f"  - `{ep['method']} {ep['path']}` → `{ep['status']}`{op}{sm}")
            if sc["asserts"]:
                a("- **asserts**:")
                for ass in sc["asserts"]:
                    a(f"  - `{ass['field']} {ass['op']} {ass['expected']}`")
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
            a("")

    # ── Workflows ────────────────────────────────────────────────────────
    a("## Workflows")
    a("")

    if doql.get("workflows"):
        doql_sources_wf = ", ".join(f"`{s}`" for s in doql.get("sources", ["app.doql.less"]))
        a(f"### DOQL Workflows ({doql_sources_wf})")
        a("")
        for wf in doql["workflows"]:
            steps = " → ".join(wf["steps"]) if wf["steps"] else "*(no steps)*"
            a(f"- **{wf['name']}** `[{wf['trigger']}]`: `{steps}`")
        a("")

    if tasks:
        a("### Taskfile Tasks (`Taskfile.yml`)")
        a("")
        a("```yaml")
        a("tasks:")
        for t in tasks:
            a(f"  {t['name']}:")
            if t["desc"]:
                a(f'    desc: "{t["desc"]}"')
            if t["cmd"]:
                a(f"    cmds:")
                a(f"      - {t['cmd']}")
        a("```")
        a("")

    # ── Quality Pipeline ─────────────────────────────────────────────────
    if pyqual:
        a("## Quality Pipeline (`pyqual.yaml`)")
        a("")
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

    # ── Configuration ────────────────────────────────────────────────────
    a("## Configuration")
    a("")
    a("```yaml")
    a("project:")
    a(f"  name: {name}")
    a(f"  version: {version}")
    a("  env: local")
    a("```")
    a("")

    # ── Dependencies ─────────────────────────────────────────────────────
    a("## Dependencies")
    a("")
    a("### Runtime")
    a("")
    for dep in deps:
        a(f"- `{dep}`")
    if not deps:
        a("- *(see pyproject.toml)*")
    a("")

    if dev_deps:
        a("### Development")
        a("")
        for dep in dev_deps:
            a(f"- `{dep}`")
        a("")

    # ── Deployment ───────────────────────────────────────────────────────
    a("## Deployment")
    a("")
    a("```bash")
    a(f"pip install {name}")
    a("")
    a("# development install")
    a("pip install -e .[dev]")
    a("```")
    a("")

    content = "\n".join(L)
    if return_sources:
        return content, sources_used
    return content
