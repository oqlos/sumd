#!/usr/bin/env python3
"""Generate SUMD.md for all projects in the oqlos workspace and validate them.

Data is extracted directly from each project's source files:
  - pyproject.toml          → name, version, description, dependencies, scripts, dev-deps
  - Taskfile.yml            → tasks with descriptions and commands  (taskfile layer)
  - testql-scenarios/*.yaml → test scenarios, types, endpoint tables (testql layer)
  - openapi.yaml            → full API surface: paths, methods, summaries, operationIds
  - app.doql.less           → DOQL declarations: app info, interfaces, integrations, workflows
  - pyqual.yaml             → quality pipeline: stages, metrics, thresholds
  - <pkg>/*.py              → Python modules in the package
  - README.md               → project title
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # pyyaml is a sumd dependency

from sumd.parser import SUMDParser, parse_file

# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def extract_pyproject(proj_dir: Path) -> dict[str, Any]:
    """Read name, version, description, dependencies, scripts from pyproject.toml."""
    toml_path = proj_dir / "pyproject.toml"
    if not toml_path.exists():
        return {}
    try:
        try:
            import tomllib
            data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except ImportError:
            import toml
            data = toml.loads(toml_path.read_text(encoding="utf-8"))
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
    except Exception as exc:
        print(f"  [WARN] pyproject.toml parse error in {proj_dir.name}: {exc}")
        return {}


def extract_taskfile(proj_dir: Path) -> list[dict[str, str]]:
    """Read tasks with descriptions and first command from Taskfile.yml."""
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
    except Exception as exc:
        print(f"  [WARN] Taskfile.yml parse error in {proj_dir.name}: {exc}")
        return []


def extract_testql_scenarios(proj_dir: Path) -> list[dict[str, Any]]:
    """Parse testql-scenarios/ files: names, types, config, endpoints, asserts."""
    scenarios_dir = proj_dir / "testql-scenarios"
    if not scenarios_dir.exists():
        return []
    scenarios = []
    for f in sorted(scenarios_dir.glob("*.yaml")):
        content = f.read_text(encoding="utf-8")

        scenario_name = re.search(r"^#\s*SCENARIO:\s*(.+)", content, re.MULTILINE)
        scenario_type = re.search(r"^#\s*TYPE:\s*(\S+)", content, re.MULTILINE)
        detectors = re.search(r"^#\s*DETECTORS:\s*(.+)", content, re.MULTILINE)
        generated = re.search(r"^#\s*GENERATED:\s*(\S+)", content, re.MULTILINE)

        # CONFIG table
        config_rows = re.findall(r"^\s{2}([a-z_]+),\s*(.+)$", content, re.MULTILINE)
        config = {k: v.strip() for k, v in config_rows if not k.startswith("detected")}

        # API endpoints table: METHOD, /path, status  # comment
        api_rows = re.findall(
            r"^\s+(GET|POST|PUT|DELETE|PATCH),\s+(/[^\s,]+),\s+(\d+)(?:\s+#\s*(\S+)\s+-\s*(.+))?",
            content, re.MULTILINE,
        )
        endpoints = []
        for method, path, status, op_id, summary in api_rows:
            ep = {"method": method, "path": path, "status": int(status)}
            if op_id:
                ep["operationId"] = op_id
            if summary:
                ep["summary"] = summary.strip()
            endpoints.append(ep)

        # ASSERT rows
        assert_rows = re.findall(
            r"^\s{2}([a-z_]+),\s*([<>=!]+),\s*(.+)$", content, re.MULTILINE
        )

        scenarios.append({
            "file": f.name,
            "name": scenario_name.group(1).strip() if scenario_name else f.stem,
            "type": scenario_type.group(1) if scenario_type else "unknown",
            "generated": generated.group(1) if generated else "false",
            "detectors": detectors.group(1).strip() if detectors else "",
            "config": config,
            "endpoints": endpoints,
            "asserts": [{"field": r[0], "op": r[1], "expected": r[2].strip()} for r in assert_rows],
        })
    return scenarios


def extract_openapi(proj_dir: Path) -> dict[str, Any]:
    """Parse openapi.yaml: info, paths with methods/summaries/operationIds/tags."""
    openapi_path = proj_dir / "openapi.yaml"
    if not openapi_path.exists():
        return {}
    try:
        data = yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
        info = data.get("info", {})
        paths = data.get("paths", {}) or {}
        endpoints = []
        seen = set()
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            # skip base_url prefixed duplicates
            if path.startswith("http"):
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
    except Exception as exc:
        print(f"  [WARN] openapi.yaml parse error in {proj_dir.name}: {exc}")
        return {}


def extract_doql(proj_dir: Path) -> dict[str, Any]:
    """Parse app.doql.less: app metadata, interfaces, integrations, workflows."""
    doql_path = proj_dir / "app.doql.less"
    if not doql_path.exists():
        return {}
    content = doql_path.read_text(encoding="utf-8")

    app_block = re.search(r"app\s*\{([^}]+)\}", content, re.DOTALL)
    app_meta = {}
    if app_block:
        for line in app_block.group(1).splitlines():
            m = re.match(r"\s*(\w+):\s*(.+?);", line)
            if m:
                app_meta[m.group(1)] = m.group(2).strip()

    # interfaces
    interfaces = []
    for m in re.finditer(r'interface\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(2)))
        interfaces.append({"selector": m.group(1).strip(), **attrs})

    # integrations
    integrations = []
    for m in re.finditer(r'integration\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(2)))
        integrations.append({"selector": m.group(1).strip(), **attrs})

    # workflows
    workflows = []
    for m in re.finditer(r'workflow\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        name_m = re.search(r'name="([^"]+)"', m.group(1))
        steps = re.findall(r'step-\d+:\s*run cmd=(.+?);', m.group(2))
        trigger_m = re.search(r'trigger:\s*(\S+?);', m.group(2))
        workflows.append({
            "name": name_m.group(1) if name_m else m.group(1),
            "trigger": trigger_m.group(1) if trigger_m else "manual",
            "steps": [s.strip() for s in steps],
        })

    return {
        "app": app_meta,
        "interfaces": interfaces,
        "integrations": integrations,
        "workflows": workflows,
    }


def extract_pyqual(proj_dir: Path) -> dict[str, Any]:
    """Parse pyqual.yaml: pipeline name, metrics/thresholds, stages."""
    pyqual_path = proj_dir / "pyqual.yaml"
    if not pyqual_path.exists():
        return {}
    try:
        data = yaml.safe_load(pyqual_path.read_text(encoding="utf-8"))
        pipeline = data.get("pipeline", data)
        metrics = pipeline.get("metrics", {})
        stages = [
            {"name": s["name"], "tool": s.get("tool", s.get("run", "")),
             "optional": s.get("optional", False)}
            for s in pipeline.get("stages", [])
            if isinstance(s, dict)
        ]
        loop = pipeline.get("loop", {})
        return {
            "name": pipeline.get("name", ""),
            "metrics": metrics,
            "stages": stages,
            "loop": loop,
        }
    except Exception as exc:
        print(f"  [WARN] pyqual.yaml parse error in {proj_dir.name}: {exc}")
        return {}


def extract_python_modules(proj_dir: Path, pkg_name: str) -> list[str]:
    """List Python source modules (non-dunder) in the package directory."""
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
# SUMD renderer — maximum LLM-useful metadata
# ---------------------------------------------------------------------------


def generate_sumd_content(proj_dir: Path) -> str:  # noqa: C901
    pkg_name = proj_dir.name

    pyproj   = extract_pyproject(proj_dir)
    tasks    = extract_taskfile(proj_dir)
    scenarios = extract_testql_scenarios(proj_dir)
    openapi  = extract_openapi(proj_dir)
    doql     = extract_doql(proj_dir)
    pyqual   = extract_pyqual(proj_dir)
    modules  = extract_python_modules(proj_dir, pkg_name)
    title    = extract_readme_title(proj_dir)

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

    # ── Title & description ──────────────────────────────────────────────
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

    # DOQL app block
    if doql.get("app"):
        a("### DOQL Application Declaration (`app.doql.less`)")
        a("")
        a("```less")
        a("app {")
        for k, v in doql["app"].items():
            a(f"  {k}: {v};")
        a("}")
        a("```")
        a("")

    if doql.get("interfaces"):
        a("### DOQL Interfaces")
        a("")
        for iface in doql["interfaces"]:
            sel = iface.pop("selector", "")
            attrs = ", ".join(f"{k}: {v}" for k, v in iface.items())
            a(f"- `interface[{sel}]` — {attrs}")
        a("")

    if doql.get("integrations"):
        a("### DOQL Integrations")
        a("")
        for intg in doql["integrations"]:
            sel = intg.pop("selector", "")
            attrs = ", ".join(f"{k}: {v}" for k, v in intg.items())
            a(f"- `integration[{sel}]` — {attrs}")
        a("")

    # Python modules
    if modules:
        a("### Source Modules")
        a("")
        for mod in modules:
            a(f"- `{name}.{mod}`")
        a("")

    # ── Interfaces ───────────────────────────────────────────────────────
    a("## Interfaces")
    a("")

    # CLI scripts
    if scripts:
        a("### CLI Entry Points")
        a("")
        for s in scripts:
            a(f"- `{s}`")
        a("")

    # OpenAPI endpoints
    if openapi.get("endpoints"):
        a("### REST API (from `openapi.yaml`)")
        a("")
        a("| Method | Path | OperationId | Summary |")
        a("|--------|------|-------------|---------|")
        for ep in openapi["endpoints"]:
            tags = ", ".join(ep.get("tags", []))
            summary = ep.get("summary", "").replace("|", "\\|")
            a(f"| `{ep['method']}` | `{ep['path']}` | `{ep['operationId']}` | {summary} |")
        a("")
        if openapi.get("schemas"):
            a("**Schemas**: " + ", ".join(f"`{s}`" for s in openapi["schemas"]))
            a("")

    # testql scenarios
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
            if sc["config"]:
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
            a("")

    # ── Workflows ────────────────────────────────────────────────────────
    a("## Workflows")
    a("")

    # DOQL workflows
    if doql.get("workflows"):
        a("### DOQL Workflows (`app.doql.less`)")
        a("")
        for wf in doql["workflows"]:
            steps = " → ".join(wf["steps"]) if wf["steps"] else "*(no steps)*"
            a(f"- **{wf['name']}** `[{wf['trigger']}]`: `{steps}`")
        a("")

    # Taskfile tasks
    if tasks:
        a("### Taskfile Tasks (`Taskfile.yml`)")
        a("")
        a("```yaml")
        a("tasks:")
        for t in tasks:
            a(f"  {t['name']}:")
            if t["desc"]:
                a(f"    desc: \"{t['desc']}\"")
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
            loop = pyqual["loop"]
            a("### Loop Behavior")
            a("")
            for k, v in loop.items():
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

    return "\n".join(L)


def main():
    base = Path("/home/tom/github/oqlos")
    parser = SUMDParser()
    results = {}

    # Auto-discover projects (dirs with pyproject.toml or Taskfile.yml)
    project_names = [
        d.name for d in sorted(base.iterdir())
        if d.is_dir()
        and not d.name.startswith(".")
        and (d / "pyproject.toml").exists()
    ]

    for proj_name in project_names:
        proj_dir = base / proj_name
        sumd_path = proj_dir / "SUMD.md"

        content = generate_sumd_content(proj_dir)
        sumd_path.write_text(content, encoding="utf-8")
        print(f"[WRITE] {sumd_path}")

        # Validate
        try:
            doc = parse_file(sumd_path)
            errors = parser.validate(doc)
            if errors:
                results[proj_name] = {"status": "INVALID", "errors": errors}
                print(f"  ❌ Validation errors: {errors}")
            else:
                results[proj_name] = {
                    "status": "OK",
                    "project_name": doc.project_name,
                    "sections": len(doc.sections),
                }
                print(f"  ✅ Valid — {doc.project_name} ({len(doc.sections)} sections)")
        except Exception as exc:
            results[proj_name] = {"status": "ERROR", "error": str(exc)}
            print(f"  ❌ Parse error: {exc}")

    # Summary JSON
    summary_path = base / "sumd-validation-report.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[REPORT] {summary_path}")

    # Export each SUMD.md to JSON
    for proj_name in project_names:
        proj_dir = base / proj_name
        sumd_path = proj_dir / "SUMD.md"
        json_path = proj_dir / "sumd.json"
        if sumd_path.exists():
            try:
                doc = parse_file(sumd_path)
                data = {
                    "project_name": doc.project_name,
                    "description": doc.description,
                    "sections": [
                        {"name": s.name, "type": s.type.value, "content": s.content, "level": s.level}
                        for s in doc.sections
                    ],
                }
                json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[EXPORT] {json_path}")
            except Exception as exc:
                print(f"[ERROR] export {proj_name}: {exc}")

    ok = all(v["status"] == "OK" for v in results.values())
    print(f"\n{'✅ All SUMD documents valid!' if ok else '❌ Some documents have issues.'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
