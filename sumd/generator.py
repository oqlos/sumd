"""SUMD Generator — extract metadata from project source files and render SUMD.md.

Sources read per project:
  pyproject.toml          → name, version, description, dependencies, scripts, python_requires
  requirements*.txt       → pip dependency lists
  setup.cfg               → legacy Python packaging metadata
  Taskfile.yml            → tasks with descriptions and commands        (taskfile layer)
  Makefile                → make targets with comments
  testql-scenarios/*.yaml → scenario names, types, endpoints, asserts   (testql layer)
  *.testql.toon.yaml      → root-level and nested toon scenario files
  openapi.yaml            → full REST API surface with operationIds      (openapi layer)
  app.doql.less           → DOQL app block, interfaces, integrations, workflows  (doql layer)
  app.doql.css            → DOQL compiled output, entities               (doql layer)
  pyqual.yaml             → quality pipeline stages and metrics
  goal.yaml               → versioning strategy, git conventions, CI hooks
  .env.example            → environment variable declarations (public)
  Dockerfile              → base image, exposed ports, entrypoint
  docker-compose*.yml     → services, ports, volumes, environment
  package.json            → Node.js name, version, scripts, dependencies
  <pkg>/*.py              → Python source modules
  README.md               → project title

Recommended companion libraries for parsing other languages/manifests:
  ruamel.yaml     — YAML round-trip parser w/ comment support
  tomli / tomllib — TOML parser (stdlib in Python 3.11+)
  orjson          — fast JSON parser
  libcst          — concrete syntax tree for Python source analysis
  tree-sitter     — incremental parser for 100+ languages (C, JS, Rust, Go...)
  semgrep         — semantic grep / pattern matching over code
  myst-parser     — extended Markdown with directives (Sphinx/docutils)
  toneformat      — token-optimised data format for LLMs
  dockerfile-parse — structured Dockerfile parser
  python-dotenv   — .env file parser
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

    # workflows: deduplicate by name (later source wins)
    # _BLOCK matches content allowing {{template}} and {single} brace expressions
    _BLOCK = r'(?:[^{}]|\{\{[^}]*\}\}|\{[^}]*\})*'
    workflows_map: dict[str, dict[str, Any]] = {}
    for m in re.finditer(r'workflow\[([^\]]+)\]\s*\{(' + _BLOCK + r')\}', content, re.DOTALL):
        name_m = re.search(r'name="([^"]+)"', m.group(1))
        wf_name = name_m.group(1) if name_m else m.group(1).strip()
        body = m.group(2)
        # steps: capture multi-line cmds, use first non-empty line as summary
        raw_steps = re.findall(r'step-\d+:\s*run cmd=(' + _BLOCK + r');', body, re.DOTALL)
        steps = []
        for s in raw_steps:
            first_line = next((l.strip() for l in s.splitlines() if l.strip()), s.strip())
            steps.append(first_line)
        trigger_m = re.search(r'trigger:\s*"?([^"\s;]+)"?;', body)
        workflows_map[wf_name] = {
            "name": wf_name,
            "trigger": trigger_m.group(1) if trigger_m else "manual",
            "steps": steps,
        }

    # interfaces: deduplicate by selector
    iface_map: dict[str, dict[str, Any]] = {}
    for iface in interfaces:
        iface_map[iface["selector"]] = iface

    return {
        "app": app_meta,
        "entities": entities,
        "interfaces": list(iface_map.values()),
        "integrations": integrations,
        "workflows": list(workflows_map.values()),
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


def extract_requirements(proj_dir: Path) -> list[dict[str, str]]:
    """Parse requirements*.txt files — return list of {file, deps[]}."""
    results = []
    for f in sorted(proj_dir.glob("requirements*.txt")):
        deps = []
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                deps.append(line)
        if deps:
            results.append({"file": f.name, "deps": deps})
    return results


def extract_makefile(proj_dir: Path) -> list[dict[str, str]]:
    """Parse Makefile — return list of {target, comment}."""
    makefile = proj_dir / "Makefile"
    if not makefile.exists():
        return []
    targets = []
    pending_comment = ""
    for line in makefile.read_text(encoding="utf-8").splitlines():
        if line.startswith("##") or line.startswith("# "):
            pending_comment = line.lstrip("#").strip()
        elif re.match(r"^[a-zA-Z0-9_-]+\s*:", line) and not line.startswith("\t"):
            target = re.match(r"^([a-zA-Z0-9_-]+)\s*:", line).group(1)
            targets.append({"target": target, "desc": pending_comment})
            pending_comment = ""
        else:
            pending_comment = ""
    return targets


def extract_goal(proj_dir: Path) -> dict[str, Any]:
    """Parse goal.yaml — versioning strategy, git conventions, build strategies."""
    goal_path = proj_dir / "goal.yaml"
    if not goal_path.exists():
        return {}
    try:
        data = yaml.safe_load(goal_path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        versioning = data.get("versioning", {})
        git = data.get("git", {})
        strategies = data.get("strategies", {})
        quality = data.get("quality", {})
        return {
            "name": project.get("name", ""),
            "type": project.get("type", []),
            "description": project.get("description", ""),
            "versioning_strategy": versioning.get("strategy", ""),
            "version_files": versioning.get("files", []),
            "commit_strategy": git.get("commit", {}).get("strategy", ""),
            "commit_scope": git.get("commit", {}).get("scope", ""),
            "changelog_template": git.get("changelog", {}).get("template", ""),
            "strategies": list(strategies.keys()),
            "quality_gates": list(quality.get("gates", {}).items()),
        }
    except Exception:
        return {}


def extract_env(proj_dir: Path) -> list[dict[str, str]]:
    """Parse .env.example — return list of {key, default, comment}."""
    for fname in (".env.example", ".env.sample", ".env.template"):
        env_path = proj_dir / fname
        if env_path.exists():
            break
    else:
        return []
    vars_: list[dict[str, str]] = []
    pending_comment = ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("#"):
            pending_comment = line_stripped.lstrip("#").strip()
        elif "=" in line_stripped:
            key, _, rest = line_stripped.partition("=")
            # split off inline comment: VALUE  # comment
            if "  #" in rest:
                val_part, inline_comment = rest.split("  #", 1)
                comment = inline_comment.strip() or pending_comment
            else:
                val_part = rest
                comment = pending_comment
            val = val_part.strip()
            vars_.append({
                "key": key.strip(),
                "default": val if val else "*(not set)*",
                "comment": comment,
            })
            pending_comment = ""
        else:
            pending_comment = ""
    return vars_


def extract_dockerfile(proj_dir: Path) -> dict[str, Any]:
    """Parse Dockerfile — base image, exposed ports, entrypoint, labels."""
    for candidate in (proj_dir / "Dockerfile", proj_dir / "docker" / "Dockerfile"):
        if candidate.exists():
            dockerfile_path = candidate
            break
    else:
        return {}
    content = dockerfile_path.read_text(encoding="utf-8")
    from_image = ""
    ports: list[str] = []
    entrypoint = ""
    cmd = ""
    labels: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if line.upper().startswith("FROM ") and not from_image:
            from_image = line[5:].strip()
        elif line.upper().startswith("EXPOSE "):
            ports.extend(line[7:].strip().split())
        elif line.upper().startswith("ENTRYPOINT "):
            entrypoint = line[11:].strip()
        elif line.upper().startswith("CMD "):
            cmd = line[4:].strip()
        elif line.upper().startswith("LABEL "):
            for kv in re.findall(r'(\w[\w.-]*)=("(?:[^"\\]|\\.)*"|\S+)', line[6:]):
                labels[kv[0]] = kv[1].strip('"')
    return {
        "from": from_image,
        "ports": ports,
        "entrypoint": entrypoint or cmd,
        "labels": labels,
    }


def extract_docker_compose(proj_dir: Path) -> dict[str, Any]:
    """Parse docker-compose*.yml — services with images, ports, environment."""
    candidates = sorted(
        list(proj_dir.glob("docker-compose*.yml"))
        + list((proj_dir / "docker").glob("docker-compose*.yml"))
    )
    if not candidates:
        return {}
    # prefer docker-compose.yml or docker-compose.dev.yml
    path = candidates[0]
    for c in candidates:
        if c.name in ("docker-compose.yml", "docker-compose.yaml"):
            path = c
            break
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        services_raw = data.get("services", {}) or {}
        services = []
        for svc_name, svc in services_raw.items():
            if not isinstance(svc, dict):
                continue
            ports = []
            for p in svc.get("ports", []):
                ports.append(str(p).strip())
            env_vars = list(svc.get("environment", {}).keys()) if isinstance(svc.get("environment"), dict) else []
            services.append({
                "name": svc_name,
                "image": svc.get("image", svc.get("build", "")),
                "ports": ports,
                "env_vars": env_vars,
            })
        return {"file": path.name, "services": services}
    except Exception:
        return {}


def extract_package_json(proj_dir: Path) -> dict[str, Any]:
    """Parse package.json — name, version, scripts, dependencies."""
    pkg = proj_dir / "package.json"
    if not pkg.exists():
        return {}
    try:
        import json
        data = json.loads(pkg.read_text(encoding="utf-8"))
        return {
            "name": data.get("name", ""),
            "version": data.get("version", ""),
            "description": data.get("description", ""),
            "main": data.get("main", ""),
            "scripts": data.get("scripts", {}),
            "dependencies": list(data.get("dependencies", {}).keys()),
            "dev_dependencies": list(data.get("devDependencies", {}).keys()),
            "engines": data.get("engines", {}),
        }
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def generate_sumd_content(  # noqa: C901
    proj_dir: Path,
    return_sources: bool = False,
    raw_sources: bool = True,
) -> str | tuple[str, list[str]]:
    """Generate SUMD.md content from a project directory.

    Args:
        proj_dir: Path to the project root.
        return_sources: If True, return (content, sources_list) instead of just content.
        raw_sources: If True (default), embed source files as raw fenced code blocks
            instead of converting them to Markdown lists/tables.
            Set to False to get structured Markdown output (parsed tables, bullet lists).

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
    reqs     = extract_requirements(proj_dir)
    makefile = extract_makefile(proj_dir)
    goal     = extract_goal(proj_dir)
    env_vars = extract_env(proj_dir)
    dockerfile = extract_dockerfile(proj_dir)
    compose  = extract_docker_compose(proj_dir)
    pkg_json = extract_package_json(proj_dir)

    # Track which source files contributed data
    if pyproj:
        sources_used.append("pyproject.toml")
    if reqs:
        sources_used.extend(r["file"] for r in reqs)
    if tasks:
        sources_used.append("Taskfile.yml")
    if makefile:
        sources_used.append("Makefile")
    if scenarios:
        sources_used.append(f"testql({len(scenarios)})")
    if openapi.get("endpoints"):
        sources_used.append(f"openapi({len(openapi['endpoints'])} ep)")
    if doql.get("app") or doql.get("workflows") or doql.get("entities"):
        sources_used.extend(doql.get("sources", ["app.doql.less"]))
    if pyqual.get("stages"):
        sources_used.append("pyqual.yaml")
    if goal.get("name"):
        sources_used.append("goal.yaml")
    if env_vars:
        sources_used.append(".env.example")
    if dockerfile:
        sources_used.append("Dockerfile")
    if compose.get("services"):
        sources_used.append(compose.get("file", "docker-compose.yml"))
    if pkg_json.get("name"):
        sources_used.append("package.json")
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

    if doql.get("app") or doql.get("entities") or doql.get("interfaces") or doql.get("workflows"):
        doql_sources = ", ".join(f"`{s}`" for s in doql.get("sources", ["app.doql.less"]))
        a(f"### DOQL Application Declaration ({doql_sources})")
        a("")
        if raw_sources:
            for fname in doql.get("sources", ["app.doql.less"]):
                fpath = proj_dir / fname
                if fpath.exists():
                    lang = "less" if fname.endswith(".less") else "css"
                    a(f"```{lang}")
                    a(fpath.read_text(encoding="utf-8").rstrip())
                    a("```")
                    a("")
        else:
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
        if raw_sources:
            op_path = proj_dir / "openapi.yaml"
            if op_path.exists():
                a("```yaml")
                a(op_path.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
        else:
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
        if raw_sources:
            seen_scenario_files: set[str] = set()
            for sc in scenarios:
                rel = sc.get("rel_path", sc["file"])
                fpath = proj_dir / rel
                if not fpath.exists() or rel in seen_scenario_files:
                    continue
                seen_scenario_files.add(rel)
                a(f"#### `{rel}`")
                a("")
                a("```toon")
                a(fpath.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
        else:
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
        if not raw_sources:
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
        if raw_sources:
            pyqual_path = proj_dir / "pyqual.yaml"
            if pyqual_path.exists():
                a("```yaml")
                a(pyqual_path.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
        else:
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
    if pkg_json.get("name"):
        a(f"```bash")
        a(f"npm install {pkg_json['name']}")
        a("```")
        a("")
    else:
        a("```bash")
        a(f"pip install {name}")
        a("")
        a("# development install")
        a("pip install -e .[dev]")
        a("```")
        a("")

    if reqs:
        a("### Requirements Files")
        a("")
        for r in reqs:
            a(f"#### `{r['file']}`")
            a("")
            for dep in r["deps"][:20]:
                a(f"- `{dep}`")
            if len(r["deps"]) > 20:
                a(f"- *(+{len(r['deps'])-20} more)*")
            a("")

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
            ports_str = ", ".join(f"`{p}`" for p in svc["ports"]) if svc["ports"] else ""
            image_str = f" image=`{svc['image']}`" if svc["image"] else ""
            a(f"- **{svc['name']}**{image_str}" + (f" ports: {ports_str}" if ports_str else ""))
        a("")

    # ── Environment ──────────────────────────────────────────────────────
    if env_vars:
        a("## Environment Variables (`.env.example`)")
        a("")
        a("| Variable | Default | Description |")
        a("|----------|---------|-------------|")
        for v in env_vars:
            desc = v["comment"].replace("|", "\\|")
            a(f"| `{v['key']}` | `{v['default']}` | {desc} |")
        a("")

    # ── Goal / Release ────────────────────────────────────────────────────
    if goal.get("name"):
        a("## Release Management (`goal.yaml`)")
        a("")
        if goal.get("versioning_strategy"):
            a(f"- **versioning**: `{goal['versioning_strategy']}`")
        if goal.get("commit_strategy"):
            a(f"- **commits**: `{goal['commit_strategy']}` scope=`{goal.get('commit_scope','')}`")
        if goal.get("changelog_template"):
            a(f"- **changelog**: `{goal['changelog_template']}`")
        if goal.get("strategies"):
            a(f"- **build strategies**: {', '.join(f'`{s}`' for s in goal['strategies'])}")
        if goal.get("version_files"):
            a(f"- **version files**: {', '.join(f'`{f}`' for f in goal['version_files'])}")
        a("")

    # ── Makefile ─────────────────────────────────────────────────────────
    if makefile:
        a("## Makefile Targets")
        a("")
        for t in makefile:
            desc = f" — {t['desc']}" if t["desc"] else ""
            a(f"- `{t['target']}`{desc}")
        a("")

    # ── package.json ─────────────────────────────────────────────────────
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
            a("**Runtime deps**: " + ", ".join(f"`{d}`" for d in pkg_json["dependencies"][:15]))
            a("")
        if pkg_json.get("engines"):
            for eng, ver in pkg_json["engines"].items():
                a(f"- **{eng}**: `{ver}`")
            a("")

    content = "\n".join(L)
    if return_sources:
        return content, sources_used
    return content

