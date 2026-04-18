"""renderer — render SUMD.md content from extracted project metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sumd.extractor import (
    extract_pyproject,
    extract_taskfile,
    extract_openapi,
    extract_doql,
    extract_pyqual,
    extract_python_modules,
    extract_readme_title,
    extract_requirements,
    extract_makefile,
    extract_goal,
    extract_env,
    extract_dockerfile,
    extract_docker_compose,
    extract_package_json,
    extract_project_analysis,
)
from sumd.toon_parser import extract_testql_scenarios


# ---------------------------------------------------------------------------
# Section renderers (private) — each returns list[str] lines
# ---------------------------------------------------------------------------


def _render_architecture(
    doql: dict, modules: list[str], name: str, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
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
                    a(f"```{lang} markpact:file path={fname}")
                    a(fpath.read_text(encoding="utf-8").rstrip())
                    a("```")
                    a("")
        else:
            _render_architecture_doql_parsed(doql, L)
    if modules:
        a("### Source Modules")
        a("")
        for mod in modules:
            a(f"- `{name}.{mod}`")
        a("")
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
            attrs_str = " — " + ", ".join(f"`{k}: {v}`" for k, v in ent["attrs"].items())
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
        attrs = ", ".join(f"{k}: {v}" for k, v in iface.items() if k not in ("selector", "page"))
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
            a("```yaml markpact:file path=openapi.yaml")
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


def _render_testql_raw(
    scenarios: list, proj_dir: Path, L: list[str]
) -> None:
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
        a(f"```toon markpact:file path={rel}")
        a(fpath.read_text(encoding="utf-8").rstrip())
        a("```")
        a("")


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


def _render_workflows(doql: dict, tasks: list, proj_dir: Path, raw_sources: bool) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Workflows")
    a("")
    if doql.get("workflows") and not raw_sources:
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
        if raw_sources:
            taskfile_path = proj_dir / "Taskfile.yml"
            if taskfile_path.exists():
                a("```yaml markpact:file path=Taskfile.yml")
                a(taskfile_path.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
        else:
            a("```yaml markpact:file path=Taskfile.yml")
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
    return L


def _render_quality(pyqual: dict, proj_dir: Path, raw_sources: bool) -> list[str]:
    if not pyqual:
        return []
    L: list[str] = []
    a = L.append
    a("## Quality Pipeline (`pyqual.yaml`)")
    a("")
    if raw_sources:
        pyqual_path = proj_dir / "pyqual.yaml"
        if pyqual_path.exists():
            a("```yaml markpact:file path=pyqual.yaml")
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
    return L


def _render_dependencies(deps: list, dev_deps: list) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Dependencies")
    a("")
    a("### Runtime")
    a("")
    if deps:
        a("```text markpact:deps python")
        for dep in deps:
            a(dep)
        a("```")
    else:
        a("*(see pyproject.toml)*")
    a("")
    if dev_deps:
        a("### Development")
        a("")
        a("```text markpact:deps python scope=dev")
        for dep in dev_deps:
            a(dep)
        a("```")
        a("")
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
            a(f"- *(+{len(r['deps'])-20} more)*")
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
            ports_str = ", ".join(f"`{p}`" for p in svc["ports"]) if svc["ports"] else ""
            image_str = f" image=`{svc['image']}`" if svc["image"] else ""
            a(f"- **{svc['name']}**{image_str}" + (f" ports: {ports_str}" if ports_str else ""))
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
            a("**Runtime deps**: " + ", ".join(f"`{d}`" for d in pkg_json["dependencies"][:15]))
            a("")
        if pkg_json.get("engines"):
            for eng, ver in pkg_json["engines"].items():
                a(f"- **{eng}**: `{ver}`")
            a("")
    return L


def _render_code_analysis(project_analysis: list) -> list[str]:
    if not project_analysis:
        return []
    L: list[str] = []
    a = L.append
    a("## Code Analysis")
    a("")
    for entry in project_analysis:
        a(f"### `{entry['file']}`")
        a("")
        lang = entry["lang"]
        if lang == "markdown":
            a(entry["content"])
        elif lang == "text":
            a(f"```text markpact:file path={entry['file']}")
            a(entry["content"])
            a("```")
        else:
            a(f"```{lang} markpact:file path={entry['file']}")
            a(entry["content"])
            a("```")
        a("")
    return L


# ---------------------------------------------------------------------------
# Main renderer helpers
# ---------------------------------------------------------------------------


def _collect_pkg_sources(
    pyproj: dict, reqs: list, tasks: list, makefile: list, scenarios: list,
    openapi: dict, doql: dict, pyqual: dict, goal: dict, env_vars: list,
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
    dockerfile: dict, compose: dict, pkg_json: dict,
    modules: list, project_analysis: list,
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
    pyproj: dict, reqs: list, tasks: list, makefile: list, scenarios: list,
    openapi: dict, doql: dict, pyqual: dict, goal: dict, env_vars: list,
    dockerfile: dict, compose: dict, pkg_json: dict, modules: list,
    project_analysis: list,
) -> list[str]:
    """Build the list of source labels that contributed data to this SUMD."""
    return (
        _collect_pkg_sources(
            pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars
        )
        + _collect_infra_sources(dockerfile, compose, pkg_json, modules, project_analysis)
    )


def _render_metadata_section(
    name: str, version: str, py_req: str, license_: str, ai_model: str,
    openapi: dict, sources_used: list[str],
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
        a(f"- **commits**: `{goal['commit_strategy']}` scope=`{goal.get('commit_scope','')}`")
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
    return re.sub(r"(\n## Metadata\n)", f"\n{toc_block}\n## Metadata\n", content, count=1)


# ---------------------------------------------------------------------------
# Main renderer
# ---------------------------------------------------------------------------


def generate_sumd_content(
    proj_dir: Path,
    return_sources: bool = False,
    raw_sources: bool = True,
) -> str | tuple[str, list[str]]:
    """Generate SUMD.md content from a project directory."""
    pkg_name = proj_dir.name

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
    project_analysis = extract_project_analysis(proj_dir)

    sources_used = _collect_sources(
        pyproj, reqs, tasks, makefile, scenarios, openapi, doql,
        pyqual, goal, env_vars, dockerfile, compose, pkg_json,
        modules, project_analysis,
    )

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

    a(f"# {title or name}")
    a("")
    a(description)
    a("")

    L.extend(_render_metadata_section(name, version, py_req, license_, ai_model, openapi, sources_used))

    a("## Intent")
    a("")
    a(description)
    a("")

    L.extend(_render_architecture(doql, modules, name, proj_dir, raw_sources))
    L.extend(_render_interfaces(scripts, openapi, scenarios, proj_dir, raw_sources))
    L.extend(_render_workflows(doql, tasks, proj_dir, raw_sources))
    L.extend(_render_quality(pyqual, proj_dir, raw_sources))
    L.extend(_render_configuration_section(name, version))
    L.extend(_render_dependencies(deps, dev_deps))
    L.extend(_render_deployment(pkg_json, name, reqs, dockerfile, compose))
    L.extend(_render_env_section(env_vars))
    L.extend(_render_goal_section(goal))
    L.extend(_render_extras(makefile, pkg_json))
    L.extend(_render_code_analysis(project_analysis))

    content = _inject_toc("\n".join(L))

    if return_sources:
        return content, sources_used
    return content
