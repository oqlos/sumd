"""SUMD CLI - Command-line interface for SUMD operations."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from sumd.parser import SUMDParser, parse_file
from sumd.generator import generate_sumd_content


@click.group()
@click.version_option(version="0.1.6")
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


@cli.command()
@click.argument("workspace", type=click.Path(exists=True, path_type=Path), default=".")
@click.option("--export-json/--no-export-json", default=True, help="Also export sumd.json per project")
@click.option("--report", type=click.Path(path_type=Path), default=None, help="Save JSON summary report to file")
@click.option("--fix/--no-fix", default=False, help="Overwrite existing SUMD.md even if already present")
@click.option("--raw/--no-raw", default=True, help="Embed source files as raw code blocks (default). Use --no-raw for structured Markdown.")
def scan(workspace: Path, export_json: bool, report: Optional[Path], fix: bool, raw: bool):
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

    project_dirs = sorted(
        d for d in workspace.iterdir()
        if d.is_dir() and not d.name.startswith(".") and (d / "pyproject.toml").exists()
    )

    if not project_dirs:
        click.echo(f"⚠️  No projects found in {workspace} (looking for directories with pyproject.toml)")
        sys.exit(1)

    click.echo(f"\n🔍 Scanning {len(project_dirs)} projects in {workspace}\n")
    click.echo(f"{'Project':<20} {'Status':<10} {'Sections':<10} {'Sources'}")
    click.echo("─" * 70)

    for proj_dir in project_dirs:
        total += 1
        sumd_path = proj_dir / "SUMD.md"

        if sumd_path.exists() and not fix:
            skip_count += 1
            click.echo(f"  {'~'} {proj_dir.name:<18} {'skip':<10} {'–':<10} already exists (use --fix to overwrite)")
            results[proj_dir.name] = {"status": "SKIP", "path": str(sumd_path)}
            continue

        try:
            content, sources = generate_sumd_content(proj_dir, return_sources=True, raw_sources=raw)
            sumd_path.write_text(content, encoding="utf-8")

            doc = parse_file(sumd_path)
            errors = parser_inst.validate(doc)

            if errors:
                fail_count += 1
                results[proj_dir.name] = {"status": "INVALID", "errors": errors, "path": str(sumd_path)}
                click.echo(f"  ❌ {proj_dir.name:<18} {'invalid':<10} {len(doc.sections):<10} {', '.join(sources)}")
                for e in errors:
                    click.echo(f"       ↳ {e}")
            else:
                ok_count += 1
                results[proj_dir.name] = {
                    "status": "OK",
                    "project_name": doc.project_name,
                    "sections": len(doc.sections),
                    "sources": sources,
                    "path": str(sumd_path),
                }
                sources_str = ", ".join(sources)
                click.echo(f"  ✅ {proj_dir.name:<18} {'ok':<10} {len(doc.sections):<10} {sources_str}")

            if export_json:
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

        except Exception as exc:
            fail_count += 1
            results[proj_dir.name] = {"status": "ERROR", "error": str(exc)}
            click.echo(f"  ❌ {proj_dir.name:<18} {'error':<10} {'–':<10} {exc}")

    click.echo("─" * 70)
    click.echo(f"\n📊 Summary: {total} projects | ✅ {ok_count} ok | ⏭ {skip_count} skipped | ❌ {fail_count} failed\n")

    if report:
        report.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        click.echo(f"📄 Report saved to {report}")

    sys.exit(0 if fail_count == 0 else 1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
