# SUMD


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.3.33-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$7.50-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-21.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $7.5000 (63 commits)
- 👤 **Human dev:** ~$2136 (21.4h @ $100/h, 30min dedup)

Generated on 2026-04-23 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

![Version](https://img.shields.io/badge/version-0.3.33-blue) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)

**SUMD** (Structured Unified Markdown Descriptor) is a semantic project descriptor format in Markdown.  
It defines intent, structure, execution entry points, and the mental model of a system for both humans and LLMs.

## What is SUMD?

SUMD is a lightweight structured markdown format that serves as a **single source of truth** for project documentation — optimised for both human readability and LLM context injection.

Think of it as a machine-readable README: a file an AI agent can parse, reason over, and act upon.

### Purpose

- **Project descriptor** — defines API, CLI, workflows, endpoints, and system architecture
- **AI context feed** — structured for LLM consumption: inject `SUMD.md` into any prompt to give the model full project understanding
- **Lightweight manifest** — bridges the gap between README, openapi spec, and configuration files
- **Automation anchor** — drives `sumd scan`, `sumd lint`, `sumd scaffold`, CI pipelines

### Use Cases

- Generating structured documentation from source code
- Single-file project context for ChatGPT, Claude, Gemini, or local LLMs
- LLM agent memory and tool context (via MCP server)
- Input for testql scenario scaffolding
- API and CLI contract documentation
- CI/CD workflow descriptions
- Structural project manifest

## Installation

```bash
pip install sumd                  # stable
pip install sumd==0.2.0rc1        # latest release candidate
```

## Developer Workflow

```bash
# health check — verify environment
task doctor

# run tests with coverage
task test

# quality gate (CC + vallm + coverage)
task pyqual

# build + publish (runs automatically when gates pass via pyqual pipeline)
task publish
```



## Usage

### CLI Commands

```bash
# Shortcut: scan current directory (detects if workspace or single project)
sumd .                          # equivalent to: sumd scan . --fix
sumd /path/to/project           # scan a specific directory

# Scan a workspace — auto-generate SUMD.md for every project found
sumd scan .                     # skip projects that already have SUMD.md
sumd scan . --fix               # overwrite existing SUMD.md
sumd reload .                   # shorthand: scan + refresh app.doql.less + doql sync
sumd scan . --fix --no-raw      # convert sources to structured Markdown instead of raw code blocks
sumd scan . --fix --analyze     # also run analysis tools (code2llm, redup, vallm)
sumd scan . --fix --analyze --tools code2llm,redup  # only selected tools
sumd scan . --fix --depth 2     # limit recursive search depth (default: unlimited)
sumd scan . --fix --no-generate-doql  # skip auto-generation of app.doql.less (enabled by default)
sumd scan . --fix --doql-sync        # refresh app.doql.less metadata, then run `doql sync` for cache-aware rebuild

# Section profiles — control how much is rendered in SUMD.md
sumd scan . --fix --profile minimal  # core sections only (metadata, architecture, workflows, dependencies, deployment)
sumd scan . --fix --profile light    # + interfaces, quality, configuration, environment, extras
sumd scan . --fix --profile rich     # + code analysis, source snippets, call graph, API stubs, test contracts (default)

# Generate SUMR.md (pre-refactoring analysis report for AI-aware refactorization)
sumd scan . --profile refactor       # creates SUMR.md — use sumr alias below
sumr .                               # shorthand: sumr <path> ≡ sumd scan <path> --fix --profile refactor

# Lint / validate SUMD files
sumd lint SUMD.md               # validate a single file
sumd lint --workspace .         # validate all SUMD.md files in the workspace
sumd lint --workspace . --json  # output JSON results

# Generate project/map.toon.yaml (static code map — without code2llm)
sumd map ./my-project             # write to project/map.toon.yaml
sumd map ./my-project --force     # overwrite existing
sumd map ./my-project --stdout    # print to stdout

# Generate testql scenario scaffolds from OpenAPI spec
sumd scaffold ./my-project                  # all scenarios (api + smoke)
sumd scaffold ./my-project --type smoke     # only smoke tests
sumd scaffold ./my-project --type crud      # per-resource CRUD scenarios
sumd scaffold ./my-project --force          # overwrite existing files

# Run analysis tools on a single project
sumd analyze ./my-project                    # run all tools
sumd analyze ./my-project --tools code2llm   # only code2llm
sumd analyze ./my-project --force            # reinstall tools
```

### Section Profiles

SUMD renders output in configurable **profiles** to trade off detail vs. token cost:

| Profile | Sections | Use case |
|---------|----------|----------|
| `minimal` | Metadata, Architecture, Workflows, Dependencies, Deployment | Quick overview, CI badges |
| `light` | + Interfaces, Quality, Configuration, Environment, Extras | Standard documentation |
| `rich` | + Code Analysis, Source Snippets, Call Graph, API Stubs, Test Contracts | LLM context injection (default) |
| `refactor` | Refactoring-focused analysis → generates `SUMR.md` | AI-aware pre-refactoring report |

### Python API

```python
from sumd import parse, parse_file
from sumd.parser import validate_sumd_file

# Parse SUMD from string
document = parse(content)

# Parse SUMD from file
document = parse_file("SUMD.md")

# Validate SUMD file (markdown structure + codeblock format)
result = validate_sumd_file(Path("SUMD.md"))
# result = {"source": "SUMD.md", "markdown": [...], "codeblocks": [...], "ok": True}
if not result["ok"]:
    for issue in result["markdown"] + result["codeblocks"]:
        print(issue)
```

## What is Embedded in SUMD.md?

SUMD auto-embeds the following sources from a project (when present):

| Source | Contents | markpact kind |
|--------|----------|---------------|
| `pyproject.toml` | metadata, deps, entry points | _parsed_ |
| `Taskfile.yml` | all tasks as raw YAML | `markpact:taskfile` |
| `openapi.yaml` | full OpenAPI spec (endpoints as sections) | `markpact:openapi` |
| `testql-scenarios/**` | all `.testql.toon.yaml` scenario files | `markpact:testql` |
| `app.doql.less` (preferred) or `.css` | DOQL styling | `markpact:doql` |
| `pyqual.yaml` | quality pipeline config | `markpact:pyqual` |
| `goal.yaml` | project intent | _rendered_ |
| `.env.example` | env variables list | _listed_ |
| `Dockerfile` | containerisation | _listed_ |
| `docker-compose.*.yml` | services | _listed_ |
| `src/**/*.py` modules | module list | _listed_ |
| `package.json` | Node.js deps (dependencies + devDependencies) | _listed_ |
| `project/analysis.toon.yaml` | static code analysis (CC, pipelines) | `markpact:analysis` |
| `project/project.toon.yaml` | project topology | `markpact:analysis` |
| `project/evolution.toon.yaml` | commit evolution | `markpact:analysis` |
| `project/map.toon.yaml` | module inventory, function signatures, CC metrics | `markpact:analysis` |
| `project/duplication.toon.yaml` | code duplication report | `markpact:analysis` |
| `project/validation.toon.yaml` | vallm validation results | `markpact:analysis` |
| `project/calls.toon.yaml` | call graph with hub metrics | `markpact:analysis` |
| `project/compact_flow.mmd` | compact call flow diagram | `markpact:analysis` |
| `project/calls.mmd` | full call graph | `markpact:analysis` |
| `project/flow.mmd` | execution flow | `markpact:analysis` |
| `project/context.md` | architecture analysis (code2llm) | _inline markdown_ |
| `project/README.md` | analysis readme | _inline markdown_ |
| `project/prompt.txt` | code2llm prompt used | `markpact:analysis` |

**Not embedded:** `*.png` (binary images), `index.html` (generated visualisation), `refactor-progress.txt`, `testql-scenarios/` inside project/.

`project/map.toon.yaml` is generated by `sumd map` (built-in, no extra deps). Other `project/` files are generated by `sumd analyze` (invokes `code2llm`, `redup`, `vallm`).


## Ecosystem Architecture

SUMD is part of a three-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│                     SUMD (opis)                              │
│              Structured Unified Markdown Descriptor          │
│         Project description, intent, architecture            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOQL (wykonanie)                          │
│              Declarative Object Query Language               │
│              Data manipulation and execution                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Taskfile (runtime)                          │
│              Task runner and workflow execution              │
│              Automation and orchestration                   │
└─────────────────────────────────────────────────────────────┘
```

- **SUMD → opis (description)**: Defines what the system is and how it should work
- **DOQL → wykonanie (execution)**: Provides the language to manipulate and execute operations
- **Taskfile → runtime**: Manages the actual execution of workflows and tasks

## DOQL Integration

SUMD can refresh `app.doql.less` metadata and optionally trigger DOQL's cache-aware rebuild.

### Generating DOQL from source

For a rich, reverse-engineered `app.doql.less` (entities, interfaces, dependencies extracted from actual code), run `doql adopt` **before** `sumd`:

```bash
doql adopt . --format less --force   # generate/update app.doql.less from source
sumd . --fix                         # consume it into SUMD.md
```

`sumd` alone generates only a minimal boilerplate. Use `doql` when you need a full declarative architecture extracted from the codebase.

### `app.doql.less` refresh behaviour

When `sumd scan . --fix` runs (or the shorthand `sumd .`):

| State | Action |
|-------|--------|
| File missing | Generates boilerplate `app.doql.less` with `app { }`, default workflows, deploy and environment blocks |
| File exists, `--fix` **not** set | Skips — existing content is preserved |
| File exists, `--fix` **set** | **Only** the `app { name; version; }` block is updated from `pyproject.toml`. All user-defined entities, interfaces, workflows, deploy and environment blocks are **preserved**. |

This means `sumd . --fix` is safe to run repeatedly — it will not destroy your custom DOQL specification.

### `doql sync` trigger

Add `--doql-sync` to run `doql sync` after SUMD generation:

```bash
sumd . --fix --doql-sync
```

Flow:
1. SUMD refreshes `app.doql.less` metadata (name/version)
2. DOQL reads the updated spec and compares it against `doql.lock`
3. If nothing changed → `✅ No changes detected — everything up to date.`
4. If sections changed → DOQL regenerates **only** the affected generators (API, web, documents, etc.)

This gives you a single command that keeps both documentation and generated code in sync, without unnecessary rebuilds.

## License

Licensed under Apache-2.0.
