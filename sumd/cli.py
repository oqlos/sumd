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
from sumd.extractor import extract_package_json, extract_pyproject
from sumd import __version__


# Language-specific boilerplate for app.doql.less generation.
# Each entry defines a minimal DOQL skeleton for a project type so that
# `sumd <dir>` produces sensible defaults for any supported language.
_DOQL_SPECS: dict[str, dict[str, str]] = {
    "python": {
        "interface": 'interface[type="cli"] {\n  framework: click;\n}',
        "install": "pip install -e .",
        "dev":     'pip install -e ".[dev]"',
        "build":   "python -m build",
        "test":    "pytest -q",
        "lint":    "ruff check .",
        "fmt":     "ruff format .",
        "clean":   "rm -rf build/ dist/ *.egg-info",
        "deploy":  "pip",
        "runtime": "python",
    },
    "node": {
        "interface": 'interface[type="web"] {\n  framework: node;\n}',
        "install": "npm install",
        "dev":     "npm run dev",
        "build":   "npm run build",
        "test":    "npm test",
        "lint":    "npm run lint",
        "fmt":     "npm run format",
        "clean":   "rm -rf node_modules dist build .cache",
        "deploy":  "npm",
        "runtime": "node",
    },
    "rust": {
        "interface": 'interface[type="cli"] {\n  framework: clap;\n}',
        "install": "cargo fetch",
        "dev":     "cargo run",
        "build":   "cargo build --release",
        "test":    "cargo test",
        "lint":    "cargo clippy --all-targets --all-features -- -D warnings",
        "fmt":     "cargo fmt",
        "clean":   "cargo clean",
        "deploy":  "cargo",
        "runtime": "rust",
    },
    "go": {
        "interface": 'interface[type="cli"] {\n  framework: cobra;\n}',
        "install": "go mod download",
        "dev":     "go run ./...",
        "build":   "go build ./...",
        "test":    "go test ./...",
        "lint":    "golangci-lint run",
        "fmt":     "gofmt -w .",
        "clean":   "go clean ./...",
        "deploy":  "go",
        "runtime": "go",
    },
    "java": {
        "interface": 'interface[type="service"] {\n  framework: spring;\n}',
        "install": "mvn install -DskipTests",
        "dev":     "mvn compile",
        "build":   "mvn package",
        "test":    "mvn test",
        "lint":    "mvn verify",
        "fmt":     "mvn spotless:apply",
        "clean":   "mvn clean",
        "deploy":  "maven",
        "runtime": "jvm",
    },
    "ruby": {
        "interface": 'interface[type="cli"] {\n  framework: thor;\n}',
        "install": "bundle install",
        "dev":     "bundle exec rake",
        "build":   "gem build *.gemspec",
        "test":    "bundle exec rspec",
        "lint":    "bundle exec rubocop",
        "fmt":     "bundle exec rubocop -a",
        "clean":   "rm -rf pkg/",
        "deploy":  "rubygems",
        "runtime": "ruby",
    },
    "php": {
        "interface": 'interface[type="web"] {\n  framework: php;\n}',
        "install": "composer install",
        "dev":     "composer dev",
        "build":   "composer build",
        "test":    "vendor/bin/phpunit",
        "lint":    "vendor/bin/phpstan analyse",
        "fmt":     "vendor/bin/php-cs-fixer fix",
        "clean":   "rm -rf vendor/",
        "deploy":  "composer",
        "runtime": "php",
    },
    "dotnet": {
        "interface": 'interface[type="cli"] {\n  framework: dotnet;\n}',
        "install": "dotnet restore",
        "dev":     "dotnet run",
        "build":   "dotnet build -c Release",
        "test":    "dotnet test",
        "lint":    "dotnet format --verify-no-changes",
        "fmt":     "dotnet format",
        "clean":   "dotnet clean",
        "deploy":  "nuget",
        "runtime": "dotnet",
    },
    "swift": {
        "interface": 'interface[type="cli"] {\n  framework: swiftpm;\n}',
        "install": "swift package resolve",
        "dev":     "swift run",
        "build":   "swift build -c release",
        "test":    "swift test",
        "lint":    "swiftlint",
        "fmt":     "swiftformat .",
        "clean":   "swift package clean",
        "deploy":  "swiftpm",
        "runtime": "swift",
    },
    "dart": {
        "interface": 'interface[type="app"] {\n  framework: flutter;\n}',
        "install": "flutter pub get",
        "dev":     "flutter run",
        "build":   "flutter build",
        "test":    "flutter test",
        "lint":    "flutter analyze",
        "fmt":     "dart format .",
        "clean":   "flutter clean",
        "deploy":  "pub",
        "runtime": "dart",
    },
    "elixir": {
        "interface": 'interface[type="service"] {\n  framework: phoenix;\n}',
        "install": "mix deps.get",
        "dev":     "iex -S mix",
        "build":   "mix compile",
        "test":    "mix test",
        "lint":    "mix credo",
        "fmt":     "mix format",
        "clean":   "mix clean",
        "deploy":  "hex",
        "runtime": "beam",
    },
    "haskell": {
        "interface": 'interface[type="cli"] {\n  framework: optparse-applicative;\n}',
        "install": "cabal build --only-dependencies",
        "dev":     "cabal run",
        "build":   "cabal build",
        "test":    "cabal test",
        "lint":    "hlint .",
        "fmt":     "ormolu --mode=inplace .",
        "clean":   "cabal clean",
        "deploy":  "hackage",
        "runtime": "haskell",
    },
    "clojure": {
        "interface": 'interface[type="cli"] {\n  framework: tools.cli;\n}',
        "install": "clj -P",
        "dev":     "clj -M:dev",
        "build":   "clj -T:build",
        "test":    "clj -M:test",
        "lint":    "clj-kondo --lint src",
        "fmt":     "cljstyle fix",
        "clean":   "rm -rf target/",
        "deploy":  "clojars",
        "runtime": "jvm",
    },
    "cpp": {
        "interface": 'interface[type="cli"] {\n  framework: native;\n}',
        "install": "cmake -S . -B build",
        "dev":     "cmake --build build",
        "build":   "cmake --build build --config Release",
        "test":    "ctest --test-dir build",
        "lint":    "clang-tidy src/*.cpp",
        "fmt":     "clang-format -i src/*",
        "clean":   "rm -rf build/",
        "deploy":  "binary",
        "runtime": "native",
    },
    "generic": {
        "interface": 'interface[type="cli"] {\n  framework: shell;\n}',
        "install": "make install",
        "dev":     "make",
        "build":   "make build",
        "test":    "make test",
        "lint":    "make lint",
        "fmt":     "make fmt",
        "clean":   "make clean",
        "deploy":  "binary",
        "runtime": "shell",
    },
}


# Ordered list of (type, markers) used to detect the dominant project type.
# First match wins — pyproject.toml before requirements.txt, etc.
_PROJECT_TYPE_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("python",   ("pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "requirements.txt")),
    ("node",     ("package.json", "deno.json", "deno.jsonc", "bun.lockb")),
    ("rust",     ("Cargo.toml",)),
    ("go",       ("go.mod",)),
    ("java",     ("pom.xml", "build.gradle", "build.gradle.kts",
                  "settings.gradle", "settings.gradle.kts", "build.sbt")),
    ("ruby",     ("Gemfile",)),
    ("php",      ("composer.json",)),
    ("swift",    ("Package.swift",)),
    ("dart",     ("pubspec.yaml",)),
    ("elixir",   ("mix.exs",)),
    ("haskell",  ("stack.yaml", "cabal.project")),
    ("clojure",  ("project.clj", "deps.edn")),
    ("cpp",      ("CMakeLists.txt", "meson.build", "configure.ac")),
)

_PROJECT_TYPE_GLOBS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("dotnet",  ("*.csproj", "*.fsproj", "*.vbproj", "*.sln")),
    ("ruby",    ("*.gemspec",)),
    ("haskell", ("*.cabal",)),
)


def _detect_project_type(proj_dir: Path) -> str:
    """Return a coarse project-type tag (python, node, rust, …) or 'generic'."""
    for type_, markers in _PROJECT_TYPE_MARKERS:
        if any((proj_dir / m).exists() for m in markers):
            return type_
    for type_, patterns in _PROJECT_TYPE_GLOBS:
        for pattern in patterns:
            try:
                if next(proj_dir.glob(pattern), None) is not None:
                    return type_
            except (PermissionError, OSError):
                continue
    return "generic"


_DOQL_AUTOGEN_MARKER = "// Generated by sumd"


def _render_doql_boilerplate(
    project_name: str,
    spec: dict[str, str],
    extra_workflows: "dict[str, str] | None" = None,
) -> str:
    """Render a full app.doql.less boilerplate from a language spec.

    extra_workflows: additional {name: cmd} pairs rendered after the canonical
                     install/dev/build/test/lint/fmt/clean set — used to surface
                     project-specific scripts (e.g. npm scripts like
                     ``icons:generate``) so the file reflects the real project.
    """
    canonical = ("install", "dev", "build", "test", "lint", "fmt", "clean")
    blocks = [
        f'workflow[name="{wf}"] {{\n  trigger: manual;\n  step-1: run cmd={spec[wf]};\n}}'
        for wf in canonical
    ]
    for name, cmd in (extra_workflows or {}).items():
        blocks.append(
            f'workflow[name="{name}"] {{\n  trigger: manual;\n  step-1: run cmd={cmd};\n}}'
        )
    workflows = "\n\n".join(blocks)
    return f'''// LESS format — define @variables here as needed
{_DOQL_AUTOGEN_MARKER} for {project_name}

{{APP_BLOCK}}

{spec["interface"]}

{workflows}

workflow[name="help"] {{
  trigger: manual;
  step-1: run cmd=task --list;
}}

deploy {{
  target: {spec["deploy"]};
}}

environment[name="local"] {{
  runtime: {spec["runtime"]};
}}
'''


# Ordered framework detectors for Node projects — first match wins.
# Entries earlier in the list are more specific (Next before React, etc.).
_NODE_FRAMEWORKS: tuple[tuple[str, frozenset[str]], ...] = (
    ("next",      frozenset({"next"})),
    ("nuxt",      frozenset({"nuxt", "nuxt3"})),
    ("astro",     frozenset({"astro"})),
    ("remix",     frozenset({"@remix-run/react", "@remix-run/node"})),
    ("sveltekit", frozenset({"@sveltejs/kit"})),
    ("svelte",    frozenset({"svelte"})),
    ("vue",       frozenset({"vue", "nuxt"})),
    ("react",     frozenset({"react"})),
    ("angular",   frozenset({"@angular/core"})),
    ("solid",     frozenset({"solid-js"})),
    ("vite",      frozenset({"vite"})),
    ("webpack",   frozenset({"webpack"})),
    ("nestjs",    frozenset({"@nestjs/core"})),
    ("fastify",   frozenset({"fastify"})),
    ("express",   frozenset({"express"})),
)


def _node_framework(deps: set[str]) -> str:
    """Derive a framework label for a Node project from its dep set."""
    base = "node"
    for fw, markers in _NODE_FRAMEWORKS:
        if deps & markers:
            base = fw
            break
    if "typescript" in deps:
        return f"{base}+typescript" if base != "node" else "typescript"
    return base


# Script names consumed by the canonical install/dev/build/test/lint/fmt/clean
# workflows — these must NOT also appear as extra workflows (would duplicate).
_NODE_CANONICAL_SCRIPTS: frozenset[str] = frozenset({
    "install", "dev", "start", "serve",
    "build", "test",
    "lint", "fmt", "format", "lint:fix",
    "clean",
})


def _node_spec_from_package_json(
    pkg_json: dict,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (spec, extra_workflows) tailored to an actual package.json.

    - Workflows reuse real npm scripts when present (``npm run <name>``) and
      fall back to sensible defaults otherwise.
    - Framework label reflects detected deps (react, vite, next, …) plus a
      ``+typescript`` suffix when TS tooling is in use.
    - Every non-canonical script is exposed as an extra workflow so the file
      mirrors the real project surface (e.g. ``icons:generate``, ``test:e2e``).
    """
    scripts: dict[str, str] = pkg_json.get("scripts") or {}
    deps: set[str] = set(pkg_json.get("dependencies") or []) | set(
        pkg_json.get("dev_dependencies") or []
    )

    framework = _node_framework(deps)
    spec = dict(_DOQL_SPECS["node"])
    spec["interface"] = f'interface[type="web"] {{\n  framework: {framework};\n}}'

    def pick(*candidates: str, fallback: str) -> str:
        for n in candidates:
            if n in scripts:
                return f"npm run {n}"
        return fallback

    spec["install"] = "npm install"
    spec["dev"]     = pick("dev", "start", "serve", fallback="npm run dev")
    spec["build"]   = pick("build", fallback="npm run build")
    spec["test"]    = "npm test" if "test" in scripts else spec["test"]
    spec["lint"]    = pick("lint", fallback="npm run lint")
    spec["fmt"]     = pick("fmt", "format", "lint:fix", fallback="npm run format")
    spec["clean"]   = pick("clean", fallback="rm -rf node_modules dist build .cache")

    extras = {
        name: f"npm run {name}"
        for name in scripts
        if name not in _NODE_CANONICAL_SCRIPTS
    }
    return spec, extras


def _build_doql_spec(
    proj_dir: Path, project_type: str,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return (spec, extra_workflows) for the given project type.

    For Node projects, the spec is derived from the actual package.json so
    the generated DOQL mirrors the real project. For every other type we
    use the static language defaults in ``_DOQL_SPECS``.
    """
    if project_type == "node":
        pkg_json = extract_package_json(proj_dir)
        if pkg_json:
            return _node_spec_from_package_json(pkg_json)
    spec = _DOQL_SPECS.get(project_type, _DOQL_SPECS["generic"])
    return dict(spec), {}


def _generate_doql_less(
    proj_dir: Path,
    project_name: str,
    version: str = "0.1.0",
    force: bool = False,
    project_type: str = "python",
) -> Path | None:
    """Generate or refresh app.doql.less file.

    - If file does not exist: create from language-appropriate boilerplate.
    - If file exists and force=False: skip (return None).
    - If file exists and force=True:
        * files originally emitted by sumd (identified by the auto-gen marker)
          are fully regenerated so they stay in sync with the project;
        * user-authored files keep all their content — only the ``app { }``
          metadata block is refreshed in place.

    Returns the path to the generated/updated file, or None if skipped.
    """
    doql_path = proj_dir / "app.doql.less"
    if doql_path.exists() and not force:
        return None

    app_block = f"""app {{\n  name: {project_name};\n  version: {version};\n}}"""

    if doql_path.exists() and force:
        content = doql_path.read_text(encoding="utf-8")
        if _DOQL_AUTOGEN_MARKER not in content:
            # User-authored: preserve body, refresh only the metadata block.
            if re.search(r"app\s*\{[^}]*\}", content, flags=re.DOTALL):
                new_content = re.sub(
                    r"app\s*\{[^}]*\}",
                    app_block,
                    content,
                    count=1,
                    flags=re.DOTALL,
                )
            else:
                new_content = app_block + "\n\n" + content
            doql_path.write_text(new_content, encoding="utf-8")
            return doql_path
        # Fall through: auto-generated → fully regenerate below.

    # Fresh boilerplate, tailored to the detected language AND project scripts.
    spec, extras = _build_doql_spec(proj_dir, project_type)
    content = _render_doql_boilerplate(project_name, spec, extras).replace(
        "{APP_BLOCK}", app_block
    )
    doql_path.write_text(content, encoding="utf-8")
    return doql_path


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
@click.option(
    "--format",
    type=click.Choice(["markdown", "json", "yaml", "toml"]),
    default="json",
    help="Output format",
)
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
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "toml"]),
    default="json",
    help="Input format",
)
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
        if data.get("description"):
            lines.append(f"{data['description']}")
        lines.append("")

        for section in data.get("sections", []):
            level_prefix = "#" * section.get("level", 2)
            lines.append(f"{level_prefix} {section['name'].title()}")
            lines.append("")
            lines.append(section.get("content", ""))
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
    ".venv",
    "venv",
    "node_modules",
    ".git",
    "__pycache__",
    ".sumd-tools",
    "site-packages",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
}


# Files whose presence marks a directory as a "project" root.
# Covers a broad range of languages and project/tooling ecosystems so that
# `sumd <dir>` works on Python, Node/JS/TS, Rust, Go, Java/Kotlin, Ruby, PHP,
# .NET, Swift, Dart/Flutter, Elixir, Haskell, Clojure, C/C++ and generic
# tool-driven repos (Taskfile, Makefile, Dockerfile, docker-compose, …).
_PROJECT_MARKER_FILES: frozenset[str] = frozenset({
    # Python
    "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "requirements.txt",
    # JavaScript / TypeScript / Node / Deno / Bun
    "package.json", "deno.json", "deno.jsonc", "bun.lockb",
    # Rust
    "Cargo.toml",
    # Go
    "go.mod",
    # Java / Kotlin / Scala / Groovy
    "pom.xml", "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts", "build.sbt",
    # Ruby
    "Gemfile",
    # PHP
    "composer.json",
    # Swift / Apple
    "Package.swift",
    # Dart / Flutter
    "pubspec.yaml",
    # Elixir
    "mix.exs",
    # Haskell
    "stack.yaml", "cabal.project",
    # Clojure
    "project.clj", "deps.edn",
    # C / C++ / native
    "CMakeLists.txt", "meson.build", "configure.ac", "Makefile", "GNUmakefile",
    # Generic / DevOps
    "Taskfile.yml", "Taskfile.yaml",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    # SUMD-specific markers (already-described projects)
    "SUMD.md", "SUMR.md", "app.doql.less", "app.doql.css", "goal.yaml",
})

# Glob patterns for project markers (extensions that vary per project).
_PROJECT_MARKER_GLOBS: tuple[str, ...] = (
    "*.csproj", "*.fsproj", "*.vbproj", "*.sln",   # .NET
    "*.gemspec",                                    # Ruby gems
    "*.cabal",                                      # Haskell
    "*.podspec",                                    # CocoaPods
)


def _is_project_dir(d: Path) -> bool:
    """Return True if *d* contains any known project-marker file."""
    try:
        names = {p.name for p in d.iterdir() if p.is_file()}
    except (PermissionError, OSError):
        return False
    if names & _PROJECT_MARKER_FILES:
        return True
    for pattern in _PROJECT_MARKER_GLOBS:
        try:
            if next(d.glob(pattern), None) is not None:
                return True
        except (PermissionError, OSError):
            continue
    return False


def _walk_projects(
    path: Path, projects: list[Path], max_depth: int | None, depth: int
) -> None:
    """Recursively collect project directories (containing any known marker)."""
    if max_depth is not None and depth > max_depth:
        return
    try:
        entries = sorted(path.iterdir(), key=lambda p: p.name)
    except PermissionError:
        return
    for d in entries:
        if not d.is_dir() or d.name.startswith(".") or d.name in _SKIP_DIRS:
            continue
        try:
            if _is_project_dir(d):
                projects.append(d)
            else:
                _walk_projects(d, projects, max_depth, depth + 1)
        except PermissionError:
            continue


def _detect_projects(workspace: Path, max_depth: int | None = None) -> list[Path]:
    """Return sorted list of subdirectories that look like project roots.

    A directory is considered a project if it contains any file listed in
    :data:`_PROJECT_MARKER_FILES` or matching :data:`_PROJECT_MARKER_GLOBS`
    (pyproject.toml, package.json, Cargo.toml, go.mod, pom.xml, Gemfile,
    composer.json, Dockerfile, Taskfile.yml, Makefile, …).
    """
    projects: list[Path] = []
    _walk_projects(workspace, projects, max_depth, 0)
    return projects


def _ensure_venv(tools_dir: Path, venv_dir: Path, tool_list: list[str]) -> None:
    """Create virtual env and install tools if not already present."""
    if venv_dir.exists():
        return
    tools_dir.mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], capture_output=True)
    pip_path = venv_dir / "bin" / "pip"
    if not pip_path.exists():
        pip_path = venv_dir / "Scripts" / "pip.exe"
    for pkg in tool_list:
        subprocess.run([str(pip_path), "install", "-q", pkg], capture_output=True)


def _tool_bin(bin_dir: Path, name: str) -> Path:
    """Return path to *name* executable, preferring non-.exe variant."""
    plain = bin_dir / name
    return plain if plain.exists() else bin_dir / f"{name}.exe"


# Tool-specific CLI argument templates
_TOOL_ARGS: dict[str, list[str]] = {
    "code2llm": ["{proj_dir}", "-f", "all", "-o", "{out}", "--no-chunk"],
    "redup":    ["scan", "{proj_dir}", "--format", "toon", "--output", "{out}"],
    "vallm":    ["batch", "{proj_dir}", "--recursive", "--format", "toon", "--output", "{out}"],
}


def _run_one_tool(tool: str, bin_dir: Path, proj_dir: Path, project_output: Path) -> None:
    """Run a single analysis tool if its arg template is known."""
    template = _TOOL_ARGS.get(tool)
    if template is None:
        return
    args = [
        a.replace("{proj_dir}", str(proj_dir)).replace("{out}", str(project_output))
        for a in template
    ]
    subprocess.run([str(_tool_bin(bin_dir, tool))] + args, capture_output=True, cwd=str(proj_dir))


def _run_analysis_tools(
    proj_dir: Path,
    tool_list: list[str],
    skip_tools: "set[str] | None" = None,
) -> None:
    """Install and run code2llm/redup/vallm analysis tools for a project.

    skip_tools: tools already run by _refresh_analysis_files() that should
                not be executed again (avoids double-running on --analyze).
    """
    skip_tools = skip_tools or set()
    tools_dir = proj_dir / ".sumd-tools"
    venv_dir = tools_dir / "venv"
    project_output = proj_dir / "project"

    _ensure_venv(tools_dir, venv_dir, tool_list)

    bin_dir = venv_dir / "bin"
    if not bin_dir.exists():
        bin_dir = venv_dir / "Scripts"

    project_output.mkdir(exist_ok=True)

    for tool in tool_list:
        if tool not in skip_tools:
            _run_one_tool(tool, bin_dir, proj_dir, project_output)


def _export_sumd_json(proj_dir: Path, doc) -> None:
    """Write sumd.json for a project."""
    json_path = proj_dir / "sumd.json"
    data = {
        "project_name": doc.project_name,
        "description": doc.description,
        "sections": [
            {
                "name": s.name,
                "type": s.type.value,
                "content": s.content,
                "level": s.level,
            }
            for s in doc.sections
        ],
    }
    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _render_write_validate(
    proj_dir: Path,
    sumd_path: Path,
    raw: bool,
    profile: str,
) -> tuple:
    """Render SUMD content, write file, validate. Returns (doc, md_issues, cb_errors, cb_warnings, sources)."""
    content, sources = RenderPipeline(proj_dir, raw_sources=raw).run(
        profile=profile, return_sources=True
    )
    sumd_path.write_text(content, encoding="utf-8")
    result = validate_sumd_file(sumd_path, profile=profile)
    md_issues = result["markdown"]
    cb_errors = [c for c in result["codeblocks"] if c.kind == "error"]
    cb_warnings = [c for c in result["codeblocks"] if c.kind == "warning"]
    doc = parse_file(sumd_path)
    return doc, md_issues, cb_errors, cb_warnings, sources


def _echo_scan_result(proj_dir: Path, doc, sources: list, cb_warnings: list) -> None:
    """Print success line for a scanned project."""
    warn_str = f" \u26a0 {len(cb_warnings)} warnings" if cb_warnings else ""
    click.echo(
        f"  \u2705 {proj_dir.name:<18} {'ok':<10} {len(doc.sections):<10} {', '.join(sources)}{warn_str}"
    )


def _maybe_generate_doql(proj_dir: Path, fix: bool) -> None:
    """Generate app.doql.less BEFORE rendering SUMD so it gets included.

    Pull name/version from the most specific manifest available and
    pick language-appropriate defaults for the boilerplate.
    """
    project_type = _detect_project_type(proj_dir)
    pyproj = extract_pyproject(proj_dir)
    pkg_json = extract_package_json(proj_dir) if project_type == "node" else {}
    project_name = (
        pyproj.get("name")
        or pkg_json.get("name")
        or proj_dir.name
    )
    version = (
        pyproj.get("version")
        or pkg_json.get("version")
        or "0.1.0"
    )
    doql_path = _generate_doql_less(
        proj_dir, project_name, version,
        force=fix, project_type=project_type,
    )
    if doql_path:
        click.echo(f"   📝 Generated {doql_path.name} ({project_type})")


def _finalize_scan(
    proj_dir: Path,
    doc,
    sources: list,
    cb_warnings: list,
    export_json: bool,
    run_analyze: bool,
    tool_list: list[str],
    doql_sync: bool,
    sumd_path: Path,
) -> dict:
    """Run post-scan actions: export JSON, run analysis, DOQL sync."""
    _echo_scan_result(proj_dir, doc, sources, cb_warnings)

    if export_json:
        _export_sumd_json(proj_dir, doc)

    if run_analyze:
        click.echo("   🔬 Running analysis...")
        _run_analysis_tools(proj_dir, tool_list)
        click.echo(f"   ✅ Analysis complete → {proj_dir / 'project'}/")

    if doql_sync and ((proj_dir / "app.doql.less").exists() or (proj_dir / "app.doql.css").exists()):
        click.echo("   ⚙️  Syncing DOQL...")
        r = subprocess.run(
            ["doql", "sync"],
            cwd=str(proj_dir),
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            click.echo("   ✅ DOQL sync complete")
        else:
            click.echo(f"   ⚠️  DOQL sync failed: {r.stderr.strip() or r.stdout.strip()}", err=True)

    return {
        "status": "OK",
        "project_name": doc.project_name,
        "sections": len(doc.sections),
        "sources": sources,
        "path": str(sumd_path),
        "warnings": [c.message for c in cb_warnings],
    }


def _scan_one_project(
    proj_dir: Path,
    fix: bool,
    raw: bool,
    export_json: bool,
    run_analyze: bool,
    tool_list: list[str],
    parser_inst: "SUMDParser",
    profile: str = "rich",
    generate_doql: bool = False,
    doql_sync: bool = False,
) -> dict:
    """Generate SUMD.md (or SUMR.md for refactor profile) for one project."""
    output_name = "SUMR.md" if profile == "refactor" else "SUMD.md"
    sumd_path = proj_dir / output_name

    if sumd_path.exists() and not fix:
        dash = "\u2013"
        click.echo(
            f"  {'~'} {proj_dir.name:<18} {'skip':<10} {dash:<10} already exists (use --fix to overwrite)"
        )
        return {"status": "SKIP", "path": str(sumd_path)}

    try:
        if generate_doql:
            _maybe_generate_doql(proj_dir, fix)

        doc, md_issues, cb_errors, cb_warnings, sources = _render_write_validate(
            proj_dir, sumd_path, raw, profile
        )
        all_errors = md_issues + [c.message for c in cb_errors]

        if all_errors:
            click.echo(
                f"  \u274c {proj_dir.name:<18} {'invalid':<10} {len(doc.sections):<10} {', '.join(sources)}"
            )
            for e in all_errors:
                click.echo(f"       \u2193 {e}")
            return {"status": "INVALID", "errors": all_errors, "path": str(sumd_path)}

        return _finalize_scan(
            proj_dir, doc, sources, cb_warnings,
            export_json, run_analyze, tool_list, doql_sync, sumd_path,
        )

    except Exception as exc:
        dash = "\u2013"
        click.echo(f"  \u274c {proj_dir.name:<18} {'error':<10} {dash:<10} {exc}")
        return {"status": "ERROR", "error": str(exc)}


@cli.command()
@click.argument("workspace", type=click.Path(exists=True, path_type=Path), default=".")
@click.option(
    "--export-json/--no-export-json",
    default=False,
    help="Also export sumd.json per project",
)
@click.option(
    "--report",
    type=click.Path(path_type=Path),
    default=None,
    help="Save JSON summary report to file",
)
@click.option(
    "--fix/--no-fix",
    default=True,
    help="Overwrite existing SUMD.md (default). Use --no-fix to skip if already present.",
)
@click.option(
    "--raw/--no-raw",
    default=True,
    help="Embed source files as raw code blocks (default). Use --no-raw for structured Markdown.",
)
@click.option(
    "--analyze/--no-analyze",
    default=False,
    help="Run analysis tools (code2llm, redup, vallm) on each project after scan",
)
@click.option(
    "--tools",
    type=str,
    default="code2llm,redup,vallm",
    help="Tools to run with --analyze",
)
@click.option(
    "--profile",
    type=click.Choice(["minimal", "light", "rich", "refactor"]),
    default="rich",
    help="Section profile to use when rendering SUMD.md. Use 'refactor' for pre-refactoring analysis report.",
)
@click.option(
    "--depth",
    type=int,
    default=None,
    help="Max directory depth to scan for projects (default: unlimited)",
)
@click.option(
    "--generate-doql/--no-generate-doql",
    default=True,
    help="Generate app.doql.less file for each project if it doesn't exist (default: enabled)",
)
@click.option(
    "--doql-sync/--no-doql-sync",
    default=False,
    help="Run 'doql sync' after generating SUMD.md (only in projects with app.doql.less/css)",
)
def scan(
    workspace: Path,
    export_json: bool,
    report: Optional[Path],
    fix: bool,
    raw: bool,
    analyze: bool,
    tools: str,
    profile: str,
    depth: Optional[int],
    generate_doql: bool,
    doql_sync: bool,
):
    """Scan a workspace directory and generate SUMD.md for every project found.

    Detects projects by the presence of a known marker file (pyproject.toml,
    package.json, Cargo.toml, go.mod, pom.xml, build.gradle, Gemfile,
    composer.json, Package.swift, pubspec.yaml, mix.exs, CMakeLists.txt,
    Makefile, Dockerfile, Taskfile.yml, SUMD.md, …) — see _PROJECT_MARKER_FILES
    for the full list. Language-agnostic: works on Python, JS/TS, Rust, Go,
    Java/Kotlin, Ruby, PHP, .NET, Swift, Dart, Elixir, Haskell, Clojure, C/C++
    and generic tool-driven repos.

    Extracts metadata from: pyproject.toml, package.json, Taskfile.yml,
    Makefile, testql-scenarios/, openapi.yaml, app.doql.less, pyqual.yaml,
    Dockerfile, docker-compose.yml, requirements*.txt, .env.example, goal.yaml
    and any Python source modules in the package directory.

    WORKSPACE: Root directory containing project subdirectories (default: current dir)
    """
    workspace = workspace.resolve()
    parser_inst = SUMDParser()
    results: dict = {}
    total = ok_count = skip_count = fail_count = 0
    tool_list = [t.strip() for t in tools.split(",") if t.strip()]

    project_dirs = _detect_projects(workspace, max_depth=depth)

    # If workspace itself looks like a project root, include it.
    if _is_project_dir(workspace):
        project_dirs.insert(0, workspace)

    if not project_dirs:
        click.echo(
            f"⚠️  No projects found in {workspace} "
            "(looked for pyproject.toml, package.json, Cargo.toml, go.mod, "
            "pom.xml, Gemfile, composer.json, Dockerfile, Taskfile.yml, "
            "Makefile, SUMD.md, …)"
        )
        sys.exit(1)

    click.echo(f"\n🔍 Scanning {len(project_dirs)} projects in {workspace}\n")
    click.echo(f"{'Project':<20} {'Status':<10} {'Sections':<10} {'Sources'}")
    click.echo("─" * 70)

    for proj_dir in project_dirs:
        total += 1
        result = _scan_one_project(
            proj_dir, fix, raw, export_json, analyze, tool_list, parser_inst, profile, generate_doql, doql_sync
        )
        results[proj_dir.name] = result
        if result["status"] == "SKIP":
            skip_count += 1
        elif result["status"] == "OK":
            ok_count += 1
        else:
            fail_count += 1

    click.echo("─" * 70)
    click.echo(
        f"\n📊 Summary: {total} projects | ✅ {ok_count} ok | ⏭ {skip_count} skipped | ❌ {fail_count} failed\n"
    )

    if report:
        report.write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        click.echo(f"📄 Report saved to {report}")

    sys.exit(0 if fail_count == 0 else 1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--workspace",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Validate all SUMD.md files in workspace subdirectories",
)
@click.option(
    "--json", "as_json", is_flag=True, default=False, help="Output results as JSON"
)
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
        click.echo(
            "⚠️  No SUMD.md files specified. Use sumd lint SUMD.md or --workspace .",
            err=True,
        )
        sys.exit(1)

    all_results = []
    total_errors = 0
    total_warnings = 0

    for path in paths:
        r = validate_sumd_file(path)
        all_results.append(r)
        errors = r["markdown"] + [
            c.message for c in r["codeblocks"] if c.kind == "error"
        ]
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
        click.echo(
            f"\n📊 {len(paths)} files | ❌ {total_errors} errors | ⚠ {total_warnings} warnings"
        )

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
    click.echo(
        f"{status} {path}  ({cb_count} blocks, {len(errors)} errors, {len(warnings)} warnings)"
    )
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
            capture_output=True,
            text=True,
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
        ("toon", "analysis.toon.yaml"),
        ("evolution", "evolution.toon.yaml"),
        ("context", "context.md"),
        ("calls_toon", "calls.toon.yaml"),
        ("mermaid", "flow.mmd, compact_flow.mmd"),
    ]
    all_ok = True
    for fmt, output_files in formats:
        extra = ["--no-png"] if fmt in ("mermaid", "calls") else []
        r = subprocess.run(
            [str(code2llm), "./", "-f", fmt, "-o", str(project_output)] + extra,
            capture_output=True,
            text=True,
            cwd=str(project),
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
@click.option(
    "--tools",
    type=str,
    default="code2llm,redup,vallm",
    help="Comma-separated list of tools to run",
)
@click.option(
    "--force/--no-force",
    default=False,
    help="Force reinstall tools even if venv exists",
)
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
        if _run_tool_subprocess(
            bin_dir,
            "redup",
            ["scan", str(project), "--format", "toon", "--output", str(project_output)],
        ):
            success_count += 1

    if "vallm" in tool_list:
        click.echo("✅ Running vallm...")
        if _run_tool_subprocess(
            bin_dir,
            "vallm",
            [
                "batch",
                str(project),
                "--recursive",
                "--format",
                "toon",
                "--output",
                str(project_output),
            ],
        ):
            success_count += 1

    click.echo(
        f"\n📊 Analysis complete: {success_count}/{len(tool_list)} tools succeeded"
    )
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


def _scaffold_write(
    path: Path, content: str, force: bool, generated: list[str], skipped: list[str]
) -> None:
    if path.exists() and not force:
        skipped.append(path.name)
    else:
        path.write_text(content, encoding="utf-8")
        generated.append(path.name)


def _scaffold_smoke_scenario(
    paths: dict,
    base: str,
    out_dir: Path,
    force: bool,
    generated: list[str],
    skipped: list[str],
) -> None:
    health_paths = [
        p for p in paths if any(k in p.lower() for k in ("health", "ping", "status"))
    ]
    ep_block = (
        "\n".join(f"  GET,  {p},  200" for p in health_paths[:5])
        if health_paths
        else "  GET,  /health,  200  # TODO: adjust path"
    )
    _scaffold_write(
        out_dir / "smoke-health.testql.toon.yaml",
        _api_scenario_template("smoke-health", "smoke", ep_block, base),
        force,
        generated,
        skipped,
    )


def _scaffold_crud_scenarios(
    groups: dict,
    base: str,
    out_dir: Path,
    force: bool,
    generated: list[str],
    skipped: list[str],
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
            _api_scenario_template(
                f"api-{safe_resource}", "api", "\n".join(ep_lines), base
            ),
            force,
            generated,
            skipped,
        )


def _scaffold_from_openapi(
    spec: dict,
    out_dir: Path,
    scenario_type: str,
    force: bool,
    generated: list[str],
    skipped: list[str],
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


def _scaffold_generic(
    out_dir: Path, force: bool, generated: list[str], skipped: list[str]
) -> None:
    click.echo("⚠️  No openapi.yaml found — generating generic smoke scaffold")
    content = _api_scenario_template(
        "smoke-generic",
        "smoke",
        "  GET,  /health,  200  # TODO: adjust\n  GET,  /,  200       # TODO: adjust",
        "/api/v1  # TODO: adjust base_path",
    )
    _scaffold_write(
        out_dir / "smoke-generic.testql.toon.yaml", content, force, generated, skipped
    )


@cli.command()
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for generated files (default: <project>/testql-scenarios/)",
)
@click.option(
    "--force/--no-force", default=False, help="Overwrite existing scenario files"
)
@click.option(
    "--type",
    "scenario_type",
    type=click.Choice(["api", "smoke", "crud", "all"]),
    default="all",
    help="Type of scenarios to generate",
)
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
        n_paths = _scaffold_from_openapi(
            spec, out_dir, scenario_type, force, generated, skipped
        )
        groups_count = len(
            {
                (path.strip("/").split("/")[0] or "root")
                for path in spec.get("paths", {})
            }
        )
        click.echo(f"   📋 {n_paths} paths → {groups_count} resource groups")
    else:
        _scaffold_generic(out_dir, force, generated, skipped)

    click.echo(
        f"\n📊 scaffold: {len(generated)} generated | {len(skipped)} skipped (use --force to overwrite)"
    )
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
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path (default: <project>/project/map.toon.yaml)",
)
@click.option(
    "--force/--no-force", default=False, help="Overwrite existing map.toon.yaml"
)
@click.option(
    "--stdout",
    is_flag=True,
    default=False,
    help="Print to stdout instead of writing file",
)
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
        "scan",
        "lint",
        "analyze",
        "map",
        "scaffold",
        "generate",
        "validate",
        "export",
        "extract",
        "info",
        "reload",
        "--help",
        "--version",
    }
    # reload <path>  →  scan <path> --fix --doql-sync
    if args and args[0] == "reload":
        path = args[1] if len(args) > 1 and not args[1].startswith("-") else "."
        extra = [a for a in args[1:] if a != path]
        _sys.argv = [_sys.argv[0], "scan", path, "--fix", "--doql-sync"] + extra
    elif args and args[0] not in known_commands and not args[0].startswith("-"):
        _sys.argv = [_sys.argv[0], "scan", args[0], "--fix"] + args[1:]
    cli()


def main_sumr():
    """Entry point for `sumr` command — generates SUMR.md (refactor profile).

    Usage:
        sumr .                  # generate SUMR.md in current project
        sumr /path/to/project   # generate SUMR.md in specified project
    """
    import sys as _sys

    args = _sys.argv[1:]
    # Default to current dir if no path given
    path = "."
    extra = []
    if args and not args[0].startswith("-"):
        path = args[0]
        extra = args[1:]
    else:
        extra = args
    _sys.argv = [_sys.argv[0], "scan", path, "--fix", "--profile", "refactor"] + extra
    cli()


if __name__ == "__main__":
    main()
