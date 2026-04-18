"""SUMD CLI - Command-line interface for SUMD operations."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from sumd.parser import SUMDParser, parse_file
from sumd.parser import validate_sumd_file
from sumd.generator import generate_map_toon
from sumd.pipeline import RenderPipeline

__version__ = "0.1.24"


@click.group()
@click.version_option(version=__version__)
def cli():
    """SUMD - Structured Unified Markdown Descriptor CLI."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def validate(file: Path):
    """Validate a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        parser = SUMDParser()
        errors = parser.validate(document)
        
        if errors:
            click.echo("❌ Validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)
        else:
            click.echo("✅ SUMD document is valid")
            sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error parsing file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(["markdown", "json", "yaml", "toml"]), default="json", help="Output format")
@click.option("--output", type=click.Path(path_type=Path), help="Output file path")
def export(file: Path, format: str, output: Optional[Path]):
    """Export a SUMD document to structured format.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        data = {
            "project_name": document.project_name,
            "description": document.description,
            "sections": [
                {
                    "name": section.name,
                    "type": section.type.value,
                    "content": section.content,
                    "level": section.level,
                }
                for section in document.sections
            ],
        }
        
        result = ""
        if format == "markdown":
            result = document.raw_content
        elif format == "json":
            import json
            result = json.dumps(data, indent=2)
        elif format == "yaml":
            import yaml
            result = yaml.dump(data, default_flow_style=False)
        elif format == "toml":
            import toml
            result = toml.dumps(data)
        
        if output:
            output.write_text(result, encoding="utf-8")
            click.echo(f"✅ Exported to {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error exporting file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def info(file: Path):
    """Display information about a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        click.echo(f"📦 Project: {document.project_name}")
        click.echo(f"📝 Description: {document.description}")
        click.echo(f"📑 Sections: {len(document.sections)}")
        
        for section in document.sections:
            click.echo(f"  - {section.name} ({section.type.value})")
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(["json", "yaml", "toml"]), default="json", help="Input format")
@click.option("--output", type=click.Path(path_type=Path), help="Output SUMD file path")
def generate(file: Path, format: str, output: Optional[Path]):
    """Generate a SUMD document from structured format.
    
    FILE: Path to the structured format file (json/yaml/toml)
    """
    try:
        content = file.read_text(encoding="utf-8")
        data = {}
        
        if format == "json":
            import json
            data = json.loads(content)
        elif format == "yaml":
            import yaml
            data = yaml.safe_load(content)
        elif format == "toml":
            import toml
            data = toml.loads(content)
        
        # Generate SUMD markdown
        lines = []
        lines.append(f"# {data.get('project_name', 'Untitled')}")
        if data.get('description'):
            lines.append(f"{data['description']}")
        lines.append("")
        
        for section in data.get('sections', []):
            level_prefix = "#" * section.get('level', 2)
            lines.append(f"{level_prefix} {section['name'].title()}")
            lines.append("")
            lines.append(section.get('content', ''))
            lines.append("")
        
        result = "\n".join(lines)
        
        if output:
            output.write_text(result, encoding="utf-8")
            click.echo(f"✅ Generated SUMD at {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error generating SUMD: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--section", type=str, help="Extract specific section")
def extract(file: Path, section: str):
    """Extract content from a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        if section:
            for sec in document.sections:
                if sec.name.lower() == section.lower():
                    click.echo(sec.content)
                    return
            click.echo(f"❌ Section '{section}' not found", err=True)
            sys.exit(1)
        else:
            click.echo(document.raw_content)
    except Exception as e:
        click.echo(f"❌ Error extracting content: {e}", err=True)
        sys.exit(1)


_SKIP_DIRS = {
    ".venv", "venv", "node_modules", ".git", "__pycache__",
    ".sumd-tools", "site-packages", "dist", "build", ".tox", ".mypy_cache",
}


def _detect_projects(workspace: Path, max_depth: int | None = None) -> list[Path]:
    """Return sorted list of subdirectories containing pyproject.toml (recursive)."""
    projects: list[Path] = []

    def _walk(path: Path, depth: int) -> None:
        if max_depth is not None and depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda p: p.name)
        except PermissionError:
            return
        for d in entries:
            if not d.is_dir() or d.name.startswith(".") or d.name in _SKIP_DIRS:
                continue
            if (d / "pyproject.toml").exists():
                projects.append(d)
            else:
                _walk(d, depth + 1)

    _walk(workspace, 0)
    return projects


def _run_analysis_tools(proj_dir: Path, tool_list: list[str]) -> None:
    """Install and run code2llm/redup/vallm analysis tools for a project."""
    tools_dir = proj_dir / ".sumd-tools"
    venv_dir = tools_dir / "venv"
    project_output = proj_dir / "project"

    if not venv_dir.exists():
        tools_dir.mkdir(exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], capture_output=True)
        pip_path = venv_dir / "bin" / "pip"
        if not pip_path.exists():
            pip_path = venv_dir / "Scripts" / "pip.exe"
        for pkg in tool_list:
            subprocess.run([str(pip_path), "install", "-q", pkg], capture_output=True)

    bin_dir = venv_dir / "bin"
    if not bin_dir.exists():
        bin_dir = venv_dir / "Scripts"

    project_output.mkdir(exist_ok=True)

    if "code2llm" in tool_list:
        code2llm = bin_dir / ("code2llm.exe" if not (bin_dir / "code2llm").exists() else "code2llm")
        subprocess.run(
            [str(code2llm), str(proj_dir), "-f", "all", "-o", str(project_output), "--no-chunk"],
            capture_output=True, cwd=str(proj_dir),
        )

    if "redup" in tool_list:
        redup = bin_dir / ("redup.exe" if not (bin_dir / "redup").exists() else "redup")
        subprocess.run(
            [str(redup), "scan", str(proj_dir), "--format", "toon", "--output", str(project_output)],
            capture_output=True, cwd=str(proj_dir),
        )

    if "vallm" in tool_list:
        vallm = bin_dir / ("vallm.exe" if not (bin_dir / "vallm").exists() else "vallm")
        subprocess.run(
            [str(vallm), "batch", str(proj_dir), "--recursive", "--format", "toon", "--output", str(project_output)],
            capture_output=True, cwd=str(proj_dir),
        )


def _export_sumd_json(proj_dir: Path, doc) -> None:
    """Write sumd.json for a project."""
    json_path = proj_dir / "sumd.json"
    data = {
        "project_name": doc.project_name,
        "description": doc.description,
        "sections": [
            {"name": s.name, "type": s.type.value, "content": s.content, "level": s.level}
            for s in doc.sections
        ],
    }
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_write_validate(
    proj_dir: Path, sumd_path: Path, raw: bool, profile: str,
) -> tuple:
    """Render SUMD content, write file, validate. Returns (doc, md_issues, cb_errors, cb_warnings, sources)."""
    content, sources = RenderPipeline(proj_dir, raw_sources=raw).run(profile=profile, return_sources=True)
    sumd_path.write_text(content, encoding="utf-8")
    result = validate_sumd_file(sumd_path)
    md_issues = result["markdown"]
    cb_errors = [c for c in result["codeblocks"] if c.kind == "error"]
    cb_warnings = [c for c in result["codeblocks"] if c.kind == "warning"]
    doc = parse_file(sumd_path)
    return doc, md_issues, cb_errors, cb_warnings, sources


def _scan_one_project(
    proj_dir: Path, fix: bool, raw: bool, export_json: bool,
    run_analyze: bool, tool_list: list[str], parser_inst: "SUMDParser",
    profile: str = "rich",
) -> dict:
    """Generate SUMD.md for one project and return a result dict."""
    sumd_path = proj_dir / "SUMD.md"

    if sumd_path.exists() and not fix:
        dash = "\u2013"
        click.echo(f"  {'~'} {proj_dir.name:<18} {'skip':<10} {dash:<10} already exists (use --fix to overwrite)")
        return {"status": "SKIP", "path": str(sumd_path)}

    try:
        doc, md_issues, cb_errors, cb_warnings, sources = _render_write_validate(
            proj_dir, sumd_path, raw, profile
        )
        all_errors = md_issues + [c.message for c in cb_errors]

        if all_errors:
            click.echo(f"  \u274c {proj_dir.name:<18} {'invalid':<10} {len(doc.sections):<10} {', '.join(sources)}")
            for e in all_errors:
                click.echo(f"       \u2193 {e}")
            return {"status": "INVALID", "errors": all_errors, "path": str(sumd_path)}

        warn_str = f" \u26a0 {len(cb_warnings)} warnings" if cb_warnings else ""
        click.echo(f"  \u2705 {proj_dir.name:<18} {'ok':<10} {len(doc.sections):<10} {', '.join(sources)}{warn_str}")

        if export_json:
            _export_sumd_json(proj_dir, doc)

        if run_analyze:
            click.echo("   \U0001f52c Running analysis...")
            _run_analysis_tools(proj_dir, tool_list)
            click.echo(f"   \u2705 Analysis complete \u2192 {proj_dir / 'project'}/")

        return {
            "status": "OK",
            "project_name": doc.project_name,
            "sections": len(doc.sections),
            "sources": sources,
            "path": str(sumd_path),
            "warnings": [c.message for c in cb_warnings],
        }

    except Exception as exc:
        dash = "\u2013"
        click.echo(f"  \u274c {proj_dir.name:<18} {'error':<10} {dash:<10} {exc}")
        return {"status": "ERROR", "error": str(exc)}


@cli.command()
@click.argument("workspace", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--export-json/--no-export-json", default=True, help="Also export sumd.json per project")
@click.option("--report", type=click.Path(path_type=Path), default=None, help="Save JSON summary report to file")
@click.option("--fix/--no-fix", default=False, help="Overwrite existing SUMD.md even if already present")
@click.option("--raw/--no-raw", default=True, help="Embed source files as raw code blocks (default). Use --no-raw for structured Markdown.")
@click.option("--analyze/--no-analyze", default=False, help="Run analysis tools (code2llm, redup, vallm) on each project after scan")
@click.option("--tools", type=str, default="code2llm,redup,vallm", help="Tools to run with --analyze")
@click.option("--profile", type=click.Choice(["minimal", "light", "rich"]), default="rich", help="Section profile to use when rendering SUMD.md")
@click.option("--depth", type=int, default=None, help="Max directory depth to scan for projects (default: unlimited)")
def scan(workspace: Path, export_json: bool, report: Optional[Path], fix: bool, raw: bool, analyze: bool, tools: str, profile: str, depth: Optional[int]):
    """Scan a workspace directory and generate SUMD.md for every project found.

    Detects projects by presence of pyproject.toml. Extracts metadata from:
    pyproject.toml, Taskfile.yml, testql-scenarios/, openapi.yaml,
    app.doql.less, pyqual.yaml, and Python source modules.

    WORKSPACE: Root directory containing project subdirectories (default: current dir)
    """
    workspace = workspace.resolve()
    parser_inst = SUMDParser()
    results: dict = {}
    total = ok_count = skip_count = fail_count = 0
    tool_list = [t.strip() for t in tools.split(",") if t.strip()]

    project_dirs = _detect_projects(workspace, max_depth=depth)

    # If workspace itself is a project (has pyproject.toml at root), scan it directly
    if not project_dirs and (workspace / "pyproject.toml").exists():
        project_dirs = [workspace]

    if not project_dirs:
        click.echo(f"⚠️  No projects found in {workspace} (looking for directories with pyproject.toml)")
        sys.exit(1)

    click.echo(f"\n🔍 Scanning {len(project_dirs)} projects in {workspace}\n")
    click.echo(f"{'Project':<20} {'Status':<10} {'Sections':<10} {'Sources'}")
    click.echo("─" * 70)

    for proj_dir in project_dirs:
        total += 1
        result = _scan_one_project(proj_dir, fix, raw, export_json, analyze, tool_list, parser_inst, profile)
        results[proj_dir.name] = result
        if result["status"] == "SKIP":
            skip_count += 1
        elif result["status"] == "OK":
            ok_count += 1
        else:
            fail_count += 1

    click.echo("─" * 70)
    click.echo(f"\n📊 Summary: {total} projects | ✅ {ok_count} ok | ⏭ {skip_count} skipped | ❌ {fail_count} failed\n")

    if report:
        report.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        click.echo(f"📄 Report saved to {report}")

    sys.exit(0 if fail_count == 0 else 1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("--workspace", type=click.Path(exists=True, path_type=Path), default=None,
              help="Validate all SUMD.md files in workspace subdirectories")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output results as JSON")
def lint(files: tuple[Path, ...], workspace: Optional[Path], as_json: bool):
    """Validate SUMD.md files — check markdown structure and codeblock formats.

    Validates:
      - Markdown structure (H1, required H2 sections, metadata fields)
      - Codeblock formats (YAML parseable, Less/CSS braces balanced, Mermaid diagram type)
      - markpact annotations (valid kind, required path= attr for markpact:file)
      - Empty or broken blocks

    Examples:
      sumd lint SUMD.md
      sumd lint --workspace .
    """
    paths = _lint_collect_paths(files, workspace)

    if not paths:
        click.echo("⚠️  No SUMD.md files specified. Use sumd lint SUMD.md or --workspace .", err=True)
        sys.exit(1)

    all_results = []
    total_errors = 0
    total_warnings = 0

    for path in paths:
        r = validate_sumd_file(path)
        all_results.append(r)
        errors = r["markdown"] + [c.message for c in r["codeblocks"] if c.kind == "error"]
        warnings = [c for c in r["codeblocks"] if c.kind == "warning"]
        total_errors += len(errors)
        total_warnings += len(warnings)

        if as_json:
            continue

        _lint_print_result(path, r)

    if as_json:
        import json as _json
        click.echo(_json.dumps(all_results, indent=2, default=str))
    else:
        click.echo(f"\n📊 {len(paths)} files | ❌ {total_errors} errors | ⚠ {total_warnings} warnings")

    sys.exit(0 if total_errors == 0 else 1)


def _lint_collect_paths(
    files: tuple[Path, ...], workspace: Optional[Path]
) -> list[Path]:
    """Collect SUMD.md paths from explicit files and/or workspace."""
    paths: list[Path] = list(files)
    if workspace:
        ws = workspace.resolve()
        paths += sorted(
            d / "SUMD.md"
            for d in ws.iterdir()
            if d.is_dir() and not d.name.startswith(".") and (d / "SUMD.md").exists()
        )
    return paths


def _lint_print_result(path: Path, r: dict) -> None:
    """Print lint result for a single file."""
    errors = r["markdown"] + [c.message for c in r["codeblocks"] if c.kind == "error"]
    warnings = [c for c in r["codeblocks"] if c.kind == "warning"]
    status = "✅" if r["ok"] else "❌"
    cb_count = len(r["codeblocks"])
    click.echo(f"{status} {path}  ({cb_count} blocks, {len(errors)} errors, {len(warnings)} warnings)")
    for issue in r["markdown"]:
        click.echo(f"    [markdown] ❌ {issue}")
    for cb in r["codeblocks"]:
        icon = "❌" if cb.kind == "error" else "⚠"
        click.echo(f"    [codeblock L{cb.line} {cb.lang}] {icon} {cb.message}")


def _setup_tools_venv(venv_dir: Path, tool_list: list[str], force: bool) -> Path:
    """Create .sumd-tools venv and install tools if needed. Returns bin_dir."""
    tools_dir = venv_dir.parent
    if not venv_dir.exists() or force:
        click.echo("📁 Setting up tools environment...")
        tools_dir.mkdir(exist_ok=True)
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            click.echo(f"❌ Failed to create venv: {result.stderr}", err=True)
            sys.exit(1)
        pip_path = venv_dir / "bin" / "pip"
        if not pip_path.exists():
            pip_path = venv_dir / "Scripts" / "pip.exe"
        for pkg in tool_list:
            click.echo(f"   📥 Installing {pkg}...")
            subprocess.run([str(pip_path), "install", "-q", pkg], capture_output=True)
    else:
        click.echo(f"📁 Using existing venv: {venv_dir}")
    bin_dir = venv_dir / "bin"
    return bin_dir if bin_dir.exists() else venv_dir / "Scripts"


def _run_code2llm_formats(bin_dir: Path, project: Path, project_output: Path) -> bool:
    """Run code2llm for each format. Returns True if all succeeded."""
    code2llm = bin_dir / "code2llm"
    if not code2llm.exists():
        code2llm = bin_dir / "code2llm.exe"
    formats = [
        ("toon",       "analysis.toon.yaml"),
        ("evolution",  "evolution.toon.yaml"),
        ("context",    "context.md"),
        ("calls_toon", "calls.toon.yaml"),
        ("mermaid",    "flow.mmd, compact_flow.mmd"),
    ]
    all_ok = True
    for fmt, output_files in formats:
        extra = ["--no-png"] if fmt in ("mermaid", "calls") else []
        r = subprocess.run(
            [str(code2llm), "./", "-f", fmt, "-o", str(project_output)] + extra,
            capture_output=True, text=True, cwd=str(project),
        )
        if r.returncode != 0:
            click.echo(f"   ⚠️  code2llm -f {fmt} failed", err=True)
            all_ok = False
        else:
            click.echo(f"   ✅ code2llm -f {fmt} → {output_files}")
    return all_ok


def _run_tool_subprocess(bin_dir: Path, tool: str, cmd_args: list[str]) -> bool:
    """Run a single analysis tool subprocess. Returns True on success."""
    exe = bin_dir / tool
    if not exe.exists():
        exe = bin_dir / f"{tool}.exe"
    r = subprocess.run([str(exe)] + cmd_args, capture_output=True, text=True)
    if r.returncode == 0:
        click.echo(f"   ✅ {tool} complete")
        return True
    click.echo(f"   ⚠️  {tool} failed", err=True)
    return False


@cli.command()
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option("--tools", type=str, default="code2llm,redup,vallm", help="Comma-separated list of tools to run")
@click.option("--force/--no-force", default=False, help="Force reinstall tools even if venv exists")
def analyze(project: Path, tools: str, force: bool):
    """Run analysis tools (code2llm, redup, vallm) on a project.

    Installs tools to .sumd-tools/venv and generates analysis files in project/.

    PROJECT: Path to the project directory to analyze
    """
    import subprocess as _sp  # noqa: F401 (already imported at top)

    project = project.resolve()
    venv_dir = project / ".sumd-tools" / "venv"
    project_output = project / "project"

    tool_list = [t.strip() for t in tools.split(",") if t.strip()]
    valid_tools = {"code2llm", "redup", "vallm"}
    invalid = set(tool_list) - valid_tools
    if invalid:
        click.echo(f"❌ Unknown tools: {', '.join(invalid)}", err=True)
        sys.exit(1)

    click.echo(f"🔍 Analyzing project: {project.name}")
    click.echo(f"📦 Tools: {', '.join(tool_list)}")

    bin_dir = _setup_tools_venv(venv_dir, tool_list, force)
    project_output.mkdir(exist_ok=True)
    success_count = 0

    if "code2llm" in tool_list:
        click.echo("🔬 Running code2llm...")
        if _run_code2llm_formats(bin_dir, project, project_output):
            success_count += 1

    if "redup" in tool_list:
        click.echo("🔍 Running redup...")
        if _run_tool_subprocess(bin_dir, "redup", [
            "scan", str(project), "--format", "toon", "--output", str(project_output)
        ]):
            success_count += 1

    if "vallm" in tool_list:
        click.echo("✅ Running vallm...")
        if _run_tool_subprocess(bin_dir, "vallm", [
            "batch", str(project), "--recursive", "--format", "toon", "--output", str(project_output)
        ]):
            success_count += 1

    click.echo(f"\n📊 Analysis complete: {success_count}/{len(tool_list)} tools succeeded")
    click.echo(f"📁 Output: {project_output}/")
    sys.exit(0 if success_count == len(tool_list) else 1)


def _api_scenario_template(
    name: str, scenario_type: str, endpoints_block: str, base_path: str = "/api/v1"
) -> str:
    n_ep = endpoints_block.strip().count("\n  ") + 1
    return (
        f"# SCENARIO: {name}.testql.toon.yaml — {name.replace('-', ' ')}\n"
        f"# TYPE: {scenario_type}\n"
        f"# VERSION: 1.0\n"
        f"# GENERATED: true\n"
        f"\n"
        f"# ── Konfiguracja ──────────────────────────────────────\n"
        f"CONFIG[1]{{key, value}}:\n"
        f"  base_path,  {base_path}\n"
        f"\n"
        f"# ── Wywołania API ─────────────────────────────────────\n"
        f"API[{n_ep}]{{method, endpoint, status}}:\n"
        f"{endpoints_block}\n"
        f"# ── Asercje ───────────────────────────────────────────\n"
        f"# ASSERT[0]{{field, op, expected}}:\n"
        f"#   TODO: fill in assertions\n"
    )


def _scaffold_write(path: Path, content: str, force: bool,
                    generated: list[str], skipped: list[str]) -> None:
    if path.exists() and not force:
        skipped.append(path.name)
    else:
        path.write_text(content, encoding="utf-8")
        generated.append(path.name)


def _scaffold_smoke_scenario(
    paths: dict, base: str, out_dir: Path, force: bool,
    generated: list[str], skipped: list[str],
) -> None:
    health_paths = [p for p in paths if any(k in p.lower() for k in ("health", "ping", "status"))]
    ep_block = (
        "\n".join(f"  GET,  {p},  200" for p in health_paths[:5])
        if health_paths
        else "  GET,  /health,  200  # TODO: adjust path"
    )
    _scaffold_write(
        out_dir / "smoke-health.testql.toon.yaml",
        _api_scenario_template("smoke-health", "smoke", ep_block, base),
        force, generated, skipped,
    )


def _scaffold_crud_scenarios(
    groups: dict, base: str, out_dir: Path, force: bool,
    generated: list[str], skipped: list[str],
) -> None:
    for resource, eps in sorted(groups.items()):
        if resource in ("health", "ping", "status"):
            continue
        safe_resource = re.sub(r"[^\w\-]", "_", resource).strip("_")
        ep_lines = [f"  {method},  {path},  200" for method, path in eps[:8]]
        if not ep_lines:
            continue
        _scaffold_write(
            out_dir / f"api-{safe_resource}.testql.toon.yaml",
            _api_scenario_template(f"api-{safe_resource}", "api", "\n".join(ep_lines), base),
            force, generated, skipped,
        )


def _scaffold_from_openapi(
    spec: dict, out_dir: Path, scenario_type: str, force: bool,
    generated: list[str], skipped: list[str],
) -> int:
    """Generate scenarios from OpenAPI spec into out_dir. Returns number of path entries."""
    paths = spec.get("paths", {})
    groups: dict[str, list[tuple[str, str]]] = {}
    for path, methods in paths.items():
        segment = path.strip("/").split("/")[0] or "root"
        for method in methods:
            if method.lower() in ("get", "post", "put", "delete", "patch"):
                groups.setdefault(segment, []).append((method.upper(), path))

    base = spec.get("servers", [{}])[0].get("url", "/api/v1").rstrip("/")

    if scenario_type in ("smoke", "all"):
        _scaffold_smoke_scenario(paths, base, out_dir, force, generated, skipped)

    if scenario_type in ("crud", "api", "all"):
        _scaffold_crud_scenarios(groups, base, out_dir, force, generated, skipped)

    return len(paths)


def _scaffold_generic(out_dir: Path, force: bool, generated: list[str], skipped: list[str]) -> None:
    click.echo("⚠️  No openapi.yaml found — generating generic smoke scaffold")
    content = _api_scenario_template(
        "smoke-generic", "smoke",
        "  GET,  /health,  200  # TODO: adjust\n  GET,  /,  200       # TODO: adjust",
        "/api/v1  # TODO: adjust base_path",
    )
    _scaffold_write(out_dir / "smoke-generic.testql.toon.yaml", content, force, generated, skipped)


@cli.command()
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option("--output", type=click.Path(path_type=Path), default=None,
              help="Output directory for generated files (default: <project>/testql-scenarios/)")
@click.option("--force/--no-force", default=False, help="Overwrite existing scenario files")
@click.option("--type", "scenario_type", type=click.Choice(["api", "smoke", "crud", "all"]),
              default="all", help="Type of scenarios to generate")
def scaffold(project: Path, output: Optional[Path], force: bool, scenario_type: str):
    """Generate testql scenario scaffolds from OpenAPI spec or SUMD.md.

    Reads openapi.yaml (if present) and generates .testql.toon.yaml scenario files
    for each endpoint group. Without OpenAPI, generates a generic smoke test scaffold.

    Why scaffold exists: sumd scan only READS existing testql files — it cannot
    generate them because testql scenarios encode expected business behaviour that
    only a human (or LLM with domain context) can define. scaffold generates the
    structural skeleton; the assertions must be filled in manually or via LLM.

    PROJECT: Path to the project directory
    """
    import yaml as _yaml

    project = project.resolve()
    out_dir = (output or (project / "testql-scenarios")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []
    skipped: list[str] = []

    openapi_path = project / "openapi.yaml"
    if openapi_path.exists():
        click.echo(f"📖 Reading {openapi_path.name}...")
        try:
            spec = _yaml.safe_load(openapi_path.read_text(encoding="utf-8"))
        except Exception as e:
            click.echo(f"❌ Failed to parse openapi.yaml: {e}", err=True)
            sys.exit(1)
        n_paths = _scaffold_from_openapi(spec, out_dir, scenario_type, force, generated, skipped)
        groups_count = len({
            (path.strip("/").split("/")[0] or "root")
            for path in spec.get("paths", {})
        })
        click.echo(f"   📋 {n_paths} paths → {groups_count} resource groups")
    else:
        _scaffold_generic(out_dir, force, generated, skipped)

    click.echo(f"\n📊 scaffold: {len(generated)} generated | {len(skipped)} skipped (use --force to overwrite)")
    for f in generated:
        click.echo(f"   ✅ {out_dir / f}")
    for f in skipped:
        click.echo(f"   ⏭  {out_dir / f} (already exists)")
    if generated:
        click.echo("\n💡 Next steps:")
        click.echo("   1. Fill in ASSERTs in generated files")
        click.echo("   2. Run: sumd scan . --fix   (to embed scenarios in SUMD.md)")
        click.echo(f"   3. Run: testql run {out_dir}/")


@cli.command(name="map")
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option("--output", type=click.Path(path_type=Path), default=None,
              help="Output file path (default: <project>/project/map.toon.yaml)")
@click.option("--force/--no-force", default=False,
              help="Overwrite existing map.toon.yaml")
@click.option("--stdout", is_flag=True, default=False,
              help="Print to stdout instead of writing file")
def map_cmd(project: Path, output: Optional[Path], force: bool, stdout: bool):
    """Generate project/map.toon.yaml — static code map in toon format.

    Analyses all source files in the project and produces a map.toon.yaml
    with module inventory, function signatures, CC estimates, and fan-out
    metrics. The file is automatically included in SUMD.md by 'sumd scan'.

    Equivalent to the 'code2llm map' output but generated without external tools.
    """
    project = project.resolve()
    out_path = output or (project / "project" / "map.toon.yaml")

    if not stdout and out_path.exists() and not force:
        click.echo(f"⏭  {out_path} already exists (use --force to overwrite)")
        sys.exit(0)

    click.echo(f"🗺  Generating map for {project.name}...")
    content = generate_map_toon(project)

    if stdout:
        click.echo(content, nl=False)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    # Quick summary from the header line
    header = content.splitlines()[0] if content else ""
    click.echo(f"✅ Written {out_path}")
    click.echo(f"   {header}")
    click.echo("\n💡 Next: sumd scan . --fix  (to embed map in SUMD.md)")


def main():
    """Main entry point — if first arg is a path, run 'scan <path> --fix'."""
    import sys as _sys
    args = _sys.argv[1:]
    # If first arg looks like a path (not a known command), treat as `scan <path> --fix`
    known_commands = {
        "scan", "lint", "analyze", "map", "scaffold", "generate",
        "validate", "export", "extract", "info", "--help", "--version",
    }
    if args and args[0] not in known_commands and not args[0].startswith("-"):
        _sys.argv = [_sys.argv[0], "scan", args[0], "--fix"] + args[1:]
    cli()


if __name__ == "__main__":
    main()
