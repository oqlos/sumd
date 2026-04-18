"""extractor — read project source files and extract structured metadata."""

from __future__ import annotations

import ast
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from sumd.toon_parser import extract_testql_scenarios  # re-export


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_toml(path: Path) -> dict:
    try:
        import tomllib
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except ImportError:
        import toml
        return toml.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


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
            cmd = ""
            if cmds and isinstance(cmds[0], str):
                cmd = cmds[0]
            elif cmds and isinstance(cmds[0], dict):
                cmd = cmds[0].get("task", cmds[0].get("cmd", ""))
            result.append({"name": task_name, "desc": desc, "cmd": cmd})
        return result
    except Exception:
        return []


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


def _parse_doql_entities(content: str) -> list[dict[str, Any]]:
    """Parse entity blocks from DOQL content."""
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
    return entities


def _parse_doql_interfaces(content: str) -> list[dict[str, Any]]:
    """Parse interface and integration blocks from DOQL content."""
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
    return interfaces


def _parse_doql_workflows(content: str) -> list[dict[str, Any]]:
    """Parse workflow blocks from DOQL content, deduplicated by name."""
    # _BLOCK matches content allowing {{template}} and {single} brace expressions
    _BLOCK = r'(?:[^{}]|\{\{[^}]*\}\}|\{[^}]*\})*'
    workflows_map: dict[str, dict[str, Any]] = {}
    for m in re.finditer(r'workflow\[([^\]]+)\]\s*\{(' + _BLOCK + r')\}', content, re.DOTALL):
        name_m = re.search(r'name="([^"]+)"', m.group(1))
        wf_name = name_m.group(1) if name_m else m.group(1).strip()
        body = m.group(2)
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
    return list(workflows_map.values())


def _parse_doql_content(content: str) -> dict[str, Any]:
    """Parse DOQL content from .less or .css file into structured data."""
    app_block = re.search(r"app\s*\{([^}]+)\}", content, re.DOTALL)
    app_meta: dict[str, str] = {}
    if app_block:
        for line in app_block.group(1).splitlines():
            m = re.match(r"\s*(\w+):\s*(.+?);", line)
            if m:
                app_meta[m.group(1)] = m.group(2).strip()

    integrations: list[dict[str, Any]] = []
    for m in re.finditer(r'integration\[([^\]]+)\]\s*\{([^}]+)\}', content, re.DOTALL):
        attrs = dict(re.findall(r'(\w[\w-]*):\s*([^;]+);', m.group(2)))
        integrations.append({"selector": m.group(1).strip(), **attrs})

    interfaces = _parse_doql_interfaces(content)
    # deduplicate by selector
    iface_map: dict[str, dict[str, Any]] = {i["selector"]: i for i in interfaces}

    return {
        "app": app_meta,
        "entities": _parse_doql_entities(content),
        "interfaces": list(iface_map.values()),
        "integrations": integrations,
        "workflows": _parse_doql_workflows(content),
    }


def extract_doql(proj_dir: Path) -> dict[str, Any]:
    """Read app.doql.less (preferred) or app.doql.css as fallback."""
    for fname in ("app.doql.less", "app.doql.css"):
        p = proj_dir / fname
        if p.exists():
            result = _parse_doql_content(p.read_text(encoding="utf-8"))
            result["sources"] = [fname]
            return result
    return {}


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
# Code / module analysis
# ---------------------------------------------------------------------------

_LANG_EXT: dict[str, str] = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".sh": "shell", ".bash": "shell", ".css": "css", ".less": "less",
    ".html": "html", ".yaml": "yaml", ".yml": "yaml", ".json": "json",
    ".toml": "toml", ".md": "markdown", ".rs": "rust", ".go": "go",
}

_IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", ".mypy_cache",
                "node_modules", ".tox", "dist", "build", "*.egg-info",
                ".sumd-tools", "project", "testql-scenarios"}

# Files to include in M[] (source code only, not docs/config/data)
_SOURCE_LANGS = {"python", "javascript", "typescript", "shell", "css", "less", "rust", "go"}

_CC_THRESHOLD = 10  # critical CC minimum


def _lang_of(path: Path) -> str:
    return _LANG_EXT.get(path.suffix.lower(), "other")


def _fan_out(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Count unique called names inside a function body."""
    calls: set[str] = set()
    for n in ast.walk(func_node):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                calls.add(n.func.id)
            elif isinstance(n.func, ast.Attribute):
                calls.add(n.func.attr)
    return len(calls)


def _cc_estimate(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Rough cyclomatic-complexity estimate: 1 + decision points."""
    decision = {ast.If, ast.For, ast.While, ast.ExceptHandler,
                ast.With, ast.AsyncFor, ast.AsyncWith, ast.Match}
    cc = 1
    for n in ast.walk(func_node):
        if type(n) in decision:
            cc += 1
        elif isinstance(n, ast.BoolOp):
            cc += len(n.values) - 1
    return cc


def _try_radon_cc(src: str) -> dict[str, int]:
    """Return {func_name: cc} using radon if available, else empty."""
    try:
        from radon.complexity import cc_visit  # type: ignore
        return {r.name: r.complexity for r in cc_visit(src)}
    except Exception:
        return {}


def _analyse_py_top_funcs(
    tree: ast.AST, radon_cc: dict[str, int]
) -> tuple[list[str], list[dict]]:
    """Extract top-level function info. Returns (exports, funcs)."""
    exports: list[str] = []
    funcs: list[dict] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            exports.append(name)
            args = [a.arg for a in node.args.args]
            cc = radon_cc.get(name) or _cc_estimate(node)
            fo = _fan_out(node)
            funcs.append({"name": name, "args": args, "cc": cc, "fan": fo})
    return exports, funcs


def _analyse_py_top_classes(
    tree: ast.AST, radon_cc: dict[str, int]
) -> tuple[list[str], list[dict]]:
    """Extract top-level class info. Returns (exports, classes)."""
    exports: list[str] = []
    classes: list[dict] = []
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        cname = node.name
        exports.append(cname)
        methods: list[dict] = []
        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                margs = [a.arg for a in item.args.args if a.arg != "self"]
                cc = radon_cc.get(item.name) or _cc_estimate(item)
                fo = _fan_out(item)
                methods.append({"name": item.name, "args": margs, "cc": cc, "fan": fo})
        docline = ""
        if (ast.get_docstring(node) or "").strip():
            docline = "  # " + (ast.get_docstring(node) or "").splitlines()[0][:60]
        classes.append({"name": cname, "methods": methods, "doc": docline})
    return exports, classes


def _analyse_py_module(path: Path) -> dict[str, Any]:
    """Extract exports, function signatures, class info from a Python file."""
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return {"exports": [], "funcs": [], "classes": [], "cc_map": {}}
    radon_cc = _try_radon_cc(src)
    func_exports, funcs = _analyse_py_top_funcs(tree, radon_cc)
    class_exports, classes = _analyse_py_top_classes(tree, radon_cc)
    return {
        "exports": func_exports + class_exports,
        "funcs": funcs,
        "classes": classes,
        "cc_map": radon_cc,
    }


def _collect_map_files(proj_dir: Path) -> tuple[dict[str, int], list[tuple[Path, int, str]]]:
    """Collect source files for map generation. Returns (lang_counts, modules)."""
    lang_counts: dict[str, int] = {}
    modules: list[tuple[Path, int, str]] = []  # (path, lines, lang)

    def _should_skip(p: Path) -> bool:
        for part in p.parts:
            if part in _IGNORE_DIRS or part.endswith(".egg-info"):
                return True
        return False

    for f in sorted(proj_dir.rglob("*")):
        if not f.is_file() or _should_skip(f.relative_to(proj_dir)):
            continue
        lang = _lang_of(f)
        if lang == "other" or lang not in _SOURCE_LANGS:
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").count("\n") + 1
        except Exception:
            continue
        rel = f.relative_to(proj_dir)
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        modules.append((rel, lines, lang))

    return lang_counts, modules


def _render_map_detail(proj_dir: Path, modules: list[tuple[Path, int, str]]) -> tuple[
    list[tuple[Path, dict]], list[dict], list[dict], int
]:
    """Analyse Python modules for map detail section. Returns (py_modules, all_funcs, all_classes, total_cls)."""
    py_modules: list[tuple[Path, dict]] = []
    all_funcs: list[dict] = []
    all_classes: list[dict] = []
    total_cls = 0

    for rel, lines, lang in modules:
        if lang != "python":
            continue
        info = _analyse_py_module(proj_dir / rel)
        py_modules.append((rel, info))
        for f in info["funcs"]:
            all_funcs.append({**f, "mod": str(rel)})
        for c in info["classes"]:
            all_classes.append({**c, "mod": str(rel)})
            total_cls += 1

    return py_modules, all_funcs, all_classes, total_cls


def _map_cc_stats(
    all_funcs: list[dict],
) -> tuple[float, int, str, str]:
    """Compute CC stats for map header. Returns (avg_cc, critical, alerts_str, hotspots_str)."""
    cc_vals = [f["cc"] for f in all_funcs] or [1]
    avg_cc = round(sum(cc_vals) / len(cc_vals), 1)
    critical = sum(1 for c in cc_vals if c >= _CC_THRESHOLD)
    by_cc = sorted(all_funcs, key=lambda x: -x["cc"])[:5]
    by_fan = sorted(all_funcs, key=lambda x: -x["fan"])[:5]
    seen: set[str] = set()
    alert_items: list[str] = []
    for f in by_cc:
        k = f"CC {f['name']}={f['cc']}"
        if k not in seen:
            alert_items.append(k)
            seen.add(k)
    for f in by_fan:
        k = f"fan-out {f['name']}={f['fan']}"
        if k not in seen:
            alert_items.append(k)
            seen.add(k)
    hotspot_items = [f"{f['name']} fan={f['fan']}" for f in by_fan[:5]]
    alerts = "; ".join(alert_items[:5]) if alert_items else "none"
    hotspots = "; ".join(hotspot_items) if hotspot_items else "none"
    return avg_cc, critical, alerts, hotspots


def generate_map_toon(proj_dir: Path) -> str:
    """Generate project/map.toon.yaml content for proj_dir."""
    proj_dir = proj_dir.resolve()
    proj_name = proj_dir.name
    today = date.today().isoformat()

    lang_counts, modules = _collect_map_files(proj_dir)
    total_files = len(modules)
    total_lines = sum(l for _, l, _ in modules)

    py_modules, all_funcs, all_classes, total_cls = _render_map_detail(proj_dir, modules)

    total_func = len(all_funcs)
    total_mod = len(modules)

    avg_cc, critical, alerts, hotspots = _map_cc_stats(all_funcs)

    # ── Render ─────────────────────────────────────────────────────────────
    L: list[str] = []
    a = L.append

    lang_str = ",".join(f"{lang}:{cnt}"
                        for lang, cnt in sorted(lang_counts.items(), key=lambda x: -x[1]))

    a(f"# {proj_name} | {total_files}f {total_lines}L | {lang_str} | {today}")
    a(f"# stats: {total_func} func | {total_cls} cls | {total_mod} mod"
      f" | CC̄={avg_cc} | critical:{critical} | cycles:0")
    a(f"# alerts[5]: {alerts}")
    a(f"# hotspots[5]: {hotspots}")
    a(f"# evolution: baseline")
    a("# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods")

    a(f"M[{total_mod}]:")
    for rel, lines, _lang in modules:
        a(f"  {rel},{lines}")

    a("D:")
    for rel, info in py_modules:
        a(f"  {rel}:")
        if info["exports"]:
            a(f"    e: {','.join(info['exports'])}")
        for cls in info["classes"]:
            method_summary = ",".join(
                f"{m['name']}({len(m['args'])})" for m in cls["methods"]
            )
            doc = cls["doc"]
            if method_summary:
                a(f"    {cls['name']}: {method_summary}{doc}")
            else:
                a(f"    {cls['name']}:{doc}")
        for f in info["funcs"]:
            sig = ";".join(f["args"]) if f["args"] else ""
            a(f"    {f['name']}({sig})")

    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Project analysis files
# ---------------------------------------------------------------------------

_PROJECT_ANALYSIS_FILES = [
    ("map.toon.yaml",   "toon"),
    ("calls.toon.yaml", "toon"),
]


def extract_project_analysis(proj_dir: Path) -> list[dict[str, str]]:
    """Return list of {file, lang, content} for files present in project/ subdir."""
    project_dir = proj_dir / "project"
    if not project_dir.is_dir():
        return []
    results = []
    for filename, lang in _PROJECT_ANALYSIS_FILES:
        fpath = project_dir / filename
        if fpath.exists():
            results.append({
                "file": f"project/{filename}",
                "lang": lang,
                "content": fpath.read_text(encoding="utf-8").rstrip(),
            })
    return results
