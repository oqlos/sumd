# SUMD — Usage Guide

> **Version 0.3.4** | [README](../README.md) | [SPEC](../SPEC.md)

## Table of Contents

1. [Ecosystem overview](#ecosystem-overview)
2. [Installation](#installation)
3. [CLI commands](#cli-commands)
   - [sumd scan](#sumd-scan--generate-sumdmd)
   - [sumr alias](#sumr-alias--pre-refactoring-analysis)
   - [sumd lint](#sumd-lint--validate-sumdmd-files)
   - [sumd map](#sumd-map--static-code-map)
   - [sumd scaffold](#sumd-scaffold--generate-testql-skeletons)
   - [sumd analyze](#sumd-analyze--static-code-analysis)
   - [Low-level commands](#low-level-commands)
4. [Section profiles](#section-profiles)
5. [Python API](#python-api)
6. [Using SUMD with LLMs](#using-sumd-with-llms)
7. [MCP server](#mcp-server)
8. [Integration with known tools](#integration-with-known-tools)
9. [What is embedded in SUMD.md](#what-is-embedded-in-sumdmd)

---

## Ecosystem Overview

SUMD is the **description layer** in a four-layer toolchain:

| Layer | Package | Role |
|-------|---------|------|
| Description | `sumd` | Structured project descriptor for humans and LLMs |
| Data | `doql` | Declarative data queries and transformations |
| Automation | `taskfile` | Task runner, deploy, CI/CD orchestration |
| Testing | `testql` | API, GUI, and CLI interface testing |

The canonical pipeline is:

```
SUMD.md (describe) → DOQL/source (code) → Taskfile (automate) → testql (verify)
```

---

## Installation

```bash
# From PyPI
pip install sumd

# With MCP server support
pip install sumd[mcp]

# From source (development)
git clone https://github.com/oqlos/sumd
cd sumd
pip install -e ".[dev]"
```

---

## CLI Commands

### `sumd scan` — Generate SUMD.md

Scans a directory, detects Python projects (by `pyproject.toml` presence), and generates or updates `SUMD.md`.

```bash
# Smart shortcut — auto-detects workspace vs single project
sumd .
sumd /path/to/project

# Explicit scan subcommand
sumd scan .                              # skip projects that already have SUMD.md
sumd scan . --fix                        # overwrite existing SUMD.md
sumd reload .                            # shorthand: scan + refresh app.doql.less + doql sync
sumd scan . --fix --no-raw               # render sources as structured Markdown (not raw code blocks)
sumd scan . --fix --report summary.json  # write scan report to JSON
sumd scan . --fix --analyze              # also run code2llm, redup, vallm analysis
sumd scan . --fix --analyze --tools code2llm,redup  # run only selected tools
sumd scan . --fix --depth 2              # limit recursive search depth (default: unlimited)
sumd scan . --fix --no-generate-doql     # skip auto-generation of app.doql.less
sumd scan . --fix --doql-sync            # refresh app.doql.less metadata, then run `doql sync` for cache-aware rebuild

# Profile selection
sumd scan . --fix --profile minimal
sumd scan . --fix --profile light
sumd scan . --fix --profile rich         # default — recommended for LLM use
sumd scan . --fix --profile refactor     # generates SUMR.md instead of SUMD.md
```

---

### `sumr` alias — Pre-Refactoring Analysis

`sumr` is a shorthand for `sumd scan --profile refactor`. It generates `SUMR.md` — a deep analysis report designed as AI context for refactoring sessions.

```bash
sumr .                   # equivalent to: sumd scan . --profile refactor
sumr ./my-project        # single project
sumr . --fix             # overwrite existing SUMR.md
```

`SUMR.md` includes: code complexity metrics, duplication analysis, call graph, evolution history, architectural critique, testql contracts, and LLM-ready refactoring suggestions.

---

### `sumd lint` — Validate SUMD.md Files

```bash
sumd lint SUMD.md                   # validate a single file
sumd lint --workspace .             # validate all SUMD.md files in the workspace
sumd lint --workspace . --json      # output JSON (for CI integration)
```

Validators check:

| Validator | What it checks |
|-----------|---------------|
| **Markdown** | H1 presence, required sections, unclosed fenced blocks |
| **`toon`** | Required section headers (`CONFIG[...]`, `API[...]`, etc.) |
| **`yaml`** | PyYAML parsability |
| **`mermaid`** | Valid diagram type declaration |
| **`less`/`css`** | Balanced braces |
| **`bash`** | No unresolved `<YOUR_...>` placeholders |
| **`text`** | Valid pip package name format |

---

### `sumd map` — Static Code Map

Generates `project/map.toon.yaml` using `ast` + `radon` — no external dependencies required.

```bash
sumd map ./my-project             # write to project/map.toon.yaml
sumd map ./my-project --force     # overwrite existing
sumd map ./my-project --stdout    # print to stdout
```

`project/map.toon.yaml` is automatically embedded in `SUMD.md` on the next `sumd scan --fix`.

---

### `sumd scaffold` — Generate testql Skeletons

Generates `testql-scenarios/*.testql.toon.yaml` skeleton files from an OpenAPI spec or `SUMD.md`.

```bash
sumd scaffold ./my-project                           # all scenarios
sumd scaffold ./my-project --type smoke              # smoke tests only
sumd scaffold ./my-project --type crud               # per-resource CRUD scenarios
sumd scaffold ./my-project --force                   # overwrite existing files
sumd scaffold ./my-project --output ./my-scenarios/  # custom output directory
```

**Full workflow: scaffold → scan → test:**

```bash
sumd scaffold ./oqlos              # 1. generate skeletons
$EDITOR testql-scenarios/*.yaml   # 2. fill in assertions
sumd scan . --fix                  # 3. embed in SUMD.md
sumd lint --workspace .            # 4. validate
testql run testql-scenarios/       # 5. run tests
```

---

### `sumd analyze` — Static Code Analysis

Runs `code2llm`, `redup`, `vallm` and writes results to `project/`.

```bash
sumd analyze ./my-project                    # run all tools
sumd analyze ./my-project --tools code2llm   # only code2llm
sumd analyze ./my-project --force            # reinstall tools
```

| Tool | Output file(s) |
|------|---------------|
| `code2llm` | `analysis.toon.yaml`, `calls.mmd`, `flow.mmd`, `context.md` |
| `redup` | `duplication.toon.yaml` |
| `vallm` | `validation.toon.yaml` |
| `sumd map` (built-in) | `map.toon.yaml` |

---

### Low-Level Commands

```bash
sumd validate SUMD.md                          # validate; exit 1 on errors
sumd export SUMD.md                            # export to JSON (default)
sumd export SUMD.md --format yaml -o spec.yaml # export to YAML file
sumd info SUMD.md                              # show name, description, sections
sumd extract SUMD.md                           # print raw content
sumd extract SUMD.md --section Intent          # extract a specific section
sumd generate spec.json                        # generate SUMD.md from JSON/YAML/TOML
```

---

## Section Profiles

| Profile | Sections | Best for |
|---------|----------|---------|
| `minimal` | Metadata, Architecture, Workflows, Dependencies, Deployment | CI badges, quick overview |
| `light` | `minimal` + Interfaces, Quality, Configuration, Environment | Standard documentation |
| `rich` | `light` + Code Analysis, Source Snippets, Call Graph, API Stubs, Test Contracts | **LLM context injection** (default) |
| `refactor` | Analysis sections + complexity, duplication, evolution → `SUMR.md` | AI-assisted refactoring |

---

## Python API

```python
from pathlib import Path
from sumd import parse, parse_file
from sumd.parser import validate_sumd_file
from sumd.pipeline import RenderPipeline

# Parse a SUMD file
doc = parse_file(Path("SUMD.md"))
print(doc.project_name)
print(doc.description)

# Access sections
intent = next(s for s in doc.sections if s.name.lower() == "intent")
print(intent.content)

# Validate
result = validate_sumd_file(Path("SUMD.md"))
if not result["ok"]:
    for issue in result["markdown"] + result["codeblocks"]:
        print(issue)

# Generate SUMD.md from source directory
content = RenderPipeline(Path("./my-project")).run(profile="rich")
Path("./my-project/SUMD.md").write_text(content)

# Generate SUMR.md (refactor profile)
content = RenderPipeline(Path("./my-project")).run(profile="refactor")
Path("./my-project/SUMR.md").write_text(content)
```

---

## Using SUMD with LLMs

### Pattern 1: Context Injection (Chat)

```bash
sumd scan . --fix --profile rich
cat SUMD.md | pbcopy   # macOS — paste into ChatGPT, Claude, etc.
```

Prompt template:
```
<context>
{SUMD.md content}
</context>

Based on the project above, identify the most complex module and suggest refactoring priorities.
```

### Pattern 2: SUMR.md for Refactoring

```bash
sumr .
cat SUMR.md | llm "Propose a refactoring plan focused on hotspots and duplication."
```

### Pattern 3: Python API for custom LLM calls

```python
from sumd import parse_file
import openai

doc = parse_file("SUMD.md")
intent = next((s.content for s in doc.sections if s.name.lower() == "intent"), "")
architecture = next((s.content for s in doc.sections if s.name.lower() == "architecture"), "")

system_prompt = f"Project: {doc.project_name}\n\nIntent:\n{intent}\n\nArchitecture:\n{architecture}"

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "List all API endpoints and their purpose."},
    ],
)
print(response.choices[0].message.content)
```

### Pattern 4: Anthropic Claude API

```python
import anthropic
from sumd import parse_file

doc = parse_file("SUMD.md")

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system=f"You have full context for the {doc.project_name} project:\n\n{doc.raw_content}",
    messages=[{"role": "user", "content": "What testql scenarios are missing for the API?"}],
)
print(message.content[0].text)
```

### Pattern 5: Local LLM via Ollama

```bash
sumd scan . --fix --profile rich
ollama run llama3 "$(printf 'Context:\n%s\n\nQuestion: What is the main entry point?' "$(cat SUMD.md)")"
```

---

## MCP Server

SUMD ships with an MCP (Model Context Protocol) server, exposing sumd operations as callable tools to any MCP-compatible agent.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `parse_sumd` | Parse SUMD.md → structured JSON |
| `validate_sumd` | Validate structure → errors list |
| `export_sumd` | Export to json / yaml / toml / markdown |
| `list_sections` | List section names and types |
| `get_section` | Get content of a specific section |
| `info_sumd` | Project name, description, section stats |
| `generate_sumd` | Generate SUMD.md from JSON payload |

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sumd": {
      "command": "python",
      "args": ["-m", "sumd.mcp_server"],
      "env": { "PYTHONPATH": "/path/to/your/project" }
    }
  }
}
```

### Cursor / Windsurf

`.cursor/mcp.json` or `.windsurf/mcp.json`:

```json
{
  "mcpServers": {
    "sumd": {
      "command": "python",
      "args": ["-m", "sumd.mcp_server"]
    }
  }
}
```

### Continue.dev

`.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "sumd.mcp_server"]
        }
      }
    ]
  }
}
```

---

## Integration with Known Tools

### GitHub Actions

```yaml
name: SUMD
on: [push]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install sumd
      - run: sumd scan . --fix --profile rich
      - run: sumd lint --workspace . --json > sumd-report.json
      - uses: actions/upload-artifact@v4
        with: { name: sumd-report, path: sumd-report.json }
```

### pre-commit

```yaml
repos:
  - repo: local
    hooks:
      - id: sumd-lint
        name: Validate SUMD.md
        entry: sumd lint
        language: system
        files: SUMD\.md$
        pass_filenames: true
```

### Taskfile

```yaml
tasks:
  docs:
    desc: Regenerate SUMD.md
    cmds: [sumd scan . --fix --profile rich]
  docs:lint:
    desc: Validate all SUMD.md files
    cmds: [sumd lint --workspace . --json]
  docs:refactor:
    desc: Generate SUMR.md
    cmds: [sumr . --fix]
```

### VS Code tasks

`.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    { "label": "SUMD: Generate", "type": "shell", "command": "sumd scan . --fix", "group": "build" },
    { "label": "SUMD: Lint",     "type": "shell", "command": "sumd lint --workspace .", "group": "test" }
  ]
}
```

### Docker

```bash
docker run --rm -v "$PWD:/project" python:3.12-slim \
  sh -c "pip install sumd && sumd scan /project --fix"
```

---

## What is Embedded in SUMD.md

| Source | Contents | Rendering |
|--------|----------|-----------|
| `pyproject.toml` | metadata, deps, entry points | parsed |
| `Taskfile.yml` | all tasks | raw YAML block |
| `openapi.yaml` | full spec + endpoints | structured sections |
| `testql-scenarios/**/*.testql.toon.yaml` | scenario files | raw toon blocks |
| `app.doql.less` / `.css` | DOQL bindings | raw Less/CSS |

**Auto-generated:** If `app.doql.less` doesn't exist, `sumd scan` generates it automatically with standard workflows (install, dev, build, test, lint, fmt, clean, help). Use `--no-generate-doql` to disable.

**Refresh behaviour:** With `--fix` (or the shorthand `sumd .`), if `app.doql.less` already exists, only the `app { name; version; }` block is updated from `pyproject.toml`. All custom entities, interfaces, workflows, deploy and environment blocks are preserved.
| `pyqual.yaml` | quality pipeline config | raw YAML |
| `goal.yaml` | project intent | rendered prose |
| `.env.example` | env variable list | bulleted list |
| `Dockerfile` / `docker-compose.*.yml` | container config | listed |
| `src/**/*.py` modules | module names | listed |
| `package.json` | Node.js deps and scripts | listed |
| `project/analysis.toon.yaml` | CC metrics, pipeline analysis | raw toon |
| `project/map.toon.yaml` | module inventory, function signatures | raw toon |
| `project/evolution.toon.yaml` | commit history | raw toon |
| `project/duplication.toon.yaml` | duplication report | raw toon |
| `project/calls.mmd` / `flow.mmd` / `compact_flow.mmd` | Mermaid diagrams | raw mermaid |
| `project/context.md` | code2llm architecture analysis | inline markdown |

**Not embedded:** `*.png`, `index.html`, `refactor-progress.txt`, `project/testql-scenarios/`.
