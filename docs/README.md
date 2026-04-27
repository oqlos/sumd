<!-- code2docs:start --># sumd

![version](https://img.shields.io/badge/version-0.3.45-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![license](https://img.shields.io/badge/license-Apache--2.0-green)

> **SUMD** — Structured Unified Markdown Descriptor for AI-aware project documentation

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/oqlos/statement](https://github.com/oqlos/statement)

## Installation

### From PyPI

```bash
pip install sumd
```

### From Source

```bash
git clone https://github.com/oqlos/statement
cd sumd
pip install -e .
```

### Optional Extras

```bash
pip install sumd[mcp]    # mcp features
pip install sumd[dev]    # development tools
```

## Quick Start

- [TestQL Autoloop Onboarding (Windsurf MCP + aider)](./TESTQL_AUTOLOOP_ONBOARDING.md)

### CLI Usage

```bash
# Scan current directory and generate SUMD.md
sumd .

# Force overwrite existing SUMD.md
sumd scan . --fix

# Scan with refactoring profile (generates SUMR.md)
sumd scan . --fix --profile refactor

# Reload — scan + refresh app.doql.less + doql sync
sumd reload .

# Validate SUMD.md file
sumd lint SUMD.md

# Static code map
sumd map .

# Generate testql skeletons
sumd scaffold .

# Run analysis with code2llm, redup, vallm
sumd analyze . --tools code2llm,redup,vallm

# Run MCP server
sumd-mcp
```

### Python API

```python
from sumd.pipeline import ScanPipeline

# Generate SUMD.md for a project
pipeline = ScanPipeline(project_dir="./my-project")
pipeline.run()
```




## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### Source Modules

- `sumd.cli`
- `sumd.extractor`
- `sumd.generator`
- `sumd.mcp_server`
- `sumd.models`
- `sumd.parser`
- `sumd.pipeline`
- `sumd.renderer`
- `sumd.toon_parser`
- `sumd.validator`

## SWOP

SWOP — Bi-directional runtime reconciler and drift-aware state graph for full-stack systems.

### Context: `core`

**Commands** (`.swop/manifests/core/commands.yml`)
- `GenerateSUMD` → `sumd.cli`
- `ExtractSwop` → `sumd.extractor`

**Queries** (`.swop/manifests/core/queries.yml`)
- `ListProjects` → `sumd.pipeline`

**Events** (`.swop/manifests/core/events.yml`)
- `SUMDGenerated` → `sumd.generator`

## Interfaces

### CLI Entry Points

- `sumd` — main documentation scanner
- `sumr` — refactoring analysis (SUMR.md)
- `sumd-mcp` — MCP server for AI context integration

### testql Scenarios

- `testql-scenarios/generated-cli-tests.testql.toon.yaml`
- `testql-scenarios/generated-from-pytests.testql.toon.yaml`

## Workflows

Key Taskfile tasks:

| Task | Description |
|------|-------------|
| `install` | Install Python dependencies (editable) |
| `deps:update` | Upgrade all outdated packages |
| `quality` | Run pyqual quality pipeline |
| `quality:fix` | Run pyqual with auto-fix |
| `test` | Run pytest suite |
| `test:report` | Run pytest + generate HTML report |
| `lint` | Run ruff lint check |
| `fmt` | Auto-format with ruff |
| `build` | Build wheel + sdist |
| `clean` | Remove build artefacts |
| `structure` | Generate app.doql.less |
| `doql:adopt` | Reverse-engineer project structure |
| `doql:build` | Build from app.doql.less |
| `docs:build` | Build SUMD documentation |
| `version:bump` | Bump version (hatch) |
| `publish` | Publish to PyPI |
| `doctor` | Health check |

## Quality Pipeline

Uses `pyqual.yaml`:

| Stage | Metric / Threshold |
|-------|-------------------|
| Analyze | `cc_max` ≤ 15 |
| Validate | `vallm_pass_min` ≥ 60 % |
| Fix | `ruff_check`, `ruff_format`, `pfix` |
| Test | `coverage_min` ≥ 35 % |
| Push | `ensure_clean` |
| Publish | `build`, `twine upload` |

## Configuration

```yaml
project:
  name: sumd
  version: 0.3.45
  env: local
```

## Dependencies

### Runtime

- `click>=8.3.3`
- `pyyaml>=6.0.3`
- `toml>=0.10.2`
- `goal>=2.1.190`
- `costs>=0.1.50`
- `pfix>=0.1.72`

### Development

- `pytest>=9.0.3`
- `pytest-cov>=7.1.0`
- `ruff>=0.15.11`
- `build>=1.4.4`
- `twine>=6.2.0`
- `pyqual>=0.1.143`
- `mcp>=1.27.0`

## Deployment

```bash
pip install sumd
pip install -e ".[dev]"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PFIX_GIT_PREFIX` | `pfix:` | Commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | Disable `.pfix_backups/` directory |

## Release Management

- **Versioning**: `semver`
- **Commits**: `conventional` (scope = `statement`)
- **Build strategies**: `python`, `nodejs`, `rust`
- **Version files**: `VERSION`, `pyproject.toml:version`, `sumd/__init__.py:__version__`

## License

Apache-2.0 © Tom Sapletta

## API Overview

### Core Classes

- **`SUMDDocument`** — Represents a parsed SUMD document.
- **`SUMDParser`** — Parser for SUMD markdown documents.
- **`Section`** — Protocol for all SUMD section renderers.
- **`RenderContext`** — All extracted data for a project, passed to every `Section.render()`.
- **`RenderPipeline`** — Collect project data → build sections → render → inject TOC.
- **`SectionType`** — SUMD section types.
- **`InterfacesSection`** — CLI entry points and testql scenarios.
- **`RefactorAnalysisSection`** — Refactoring analysis (SUMR.md profile).
- **`QualitySection`** — Quality pipeline thresholds and checks.
- **`DeploymentSection`** — Docker, CI/CD, and deployment configuration.
- **`CodeAnalysisSection`** — Static analysis results (code2llm, redup, vallm).
- **`MetadataSection`** — Render `## Metadata` — always present, all profiles.
- **`DependenciesSection`** — Runtime and development dependencies.
- **`CallGraphSection`** — Function call graph and module relationships.
- **`ArchitectureSection`** — Project architecture and source modules.
- **`SourceSnippetsSection`** — Per-module AST summaries.
- **`WorkflowsSection`** — Taskfile tasks and automation workflows.
- **`SwopSection`** — SWOP manifests (commands, queries, events).
- **`ExtrasSection`** — Additional project-specific data.
- **`ApiStubsSection`** — API stubs and interface definitions.
- **`EnvironmentSection`** — `.env.example` and environment variables.
- **`ConfigurationSection`** — Project configuration and settings.

### Key Functions

- `scan()` — Scan a workspace directory and generate `SUMD.md`.
- `lint()` — Validate `SUMD.md` files (markdown structure, codeblock formats).
- `analyze()` — Run analysis tools (`code2llm`, `redup`, `vallm`).
- `scaffold()` — Generate testql scenario scaffolds.
- `map_cmd()` — Generate `project/map.toon.yaml` static code map.
- `extract_pyproject()` / `extract_taskfile()` / `extract_goal()` / `extract_env()` — Extractors for configuration files.
- `extract_doql()` — Read `app.doql.less` (preferred) or `app.doql.css` as fallback.
- `extract_python_modules()` — Per-module AST summary for source snippets.
- `extract_swop()` — Extract SWOP manifest files from `.swop/manifests/<context>/`.
- `extract_project_analysis()` — Files present in `project/` subdir.
- `validate_codeblocks()` — Validate fenced code blocks in content.
- `validate_markdown()` — Validate SUMD markdown structure.
- `parse()` / `parse_file()` — Parse SUMD documents.
- `generate_sumd_content()` — Generate `SUMD.md` content from a project directory.
- `main()` / `main_sumr()` — CLI entry points for `sumd` and `sumr`.


<!-- code2docs:end -->