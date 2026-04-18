# SUMD

## AI Cost Tracking

![AI Cost](https://img.shields.io/badge/AI%20Cost-$2.55-green) ![AI Model](https://img.shields.io/badge/AI%20Model-openrouter%2Fqwen%2Fqwen3-coder-next-lightgrey)

This project uses AI-generated code. Total cost: **$2.5500** with **17** AI commits.

Generated on 2026-04-18 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/models/openrouter/qwen/qwen3-coder-next)

---



SUMD is a semantic project descriptor format in Markdown that defines intent, structure, execution entry points, and mental model of a system for both humans and LLMs.

## What is SUMD?

SUMD (Structured Unified Markdown Descriptor) is a lightweight structured markdown format for AI-aware project descriptions. It serves as a single source of truth for project documentation, optimized for both human readability and LLM context injection.

### Purpose

- **Project descriptor**: Defines API, CLI, workflows, endpoints, and system architecture
- **AI-optimized**: Structured for LLM consumption and automation tools
- **Lightweight manifest**: Bridges the gap between README, spec, and configuration files
- **Context injection**: Provides structured context for AI agents and tools

### Use Cases

- Project documentation and specification
- Input for LLM context injection
- CI/CD workflow descriptions
- API and CLI mapping
- Structural project manifest

## Installation

```bash
pip install sumd
```

## Usage

### CLI Commands

```bash
# Scan a workspace — auto-generate SUMD.md for every project found
sumd scan .                     # skip projects that already have SUMD.md
sumd scan . --fix               # overwrite existing SUMD.md
sumd scan . --fix --no-raw      # convert sources to structured Markdown instead of raw code blocks
sumd scan . --fix --analyze     # also run analysis tools (code2llm, redup, vallm)
sumd scan . --fix --analyze --tools code2llm,redup  # only selected tools

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
| `Taskfile.yml` | all tasks as raw YAML | `markpact:file` |
| `openapi.yaml` | full OpenAPI spec (endpoints as sections) | `markpact:file` |
| `testql-scenarios/**` | all `.testql.toon.yaml` scenario files | `markpact:file` |
| `app.doql.less` / `.css` | DOQL styling | `markpact:file` |
| `pyqual.yaml` | quality pipeline config | `markpact:file` |
| `goal.yaml` | project intent | _rendered_ |
| `.env.example` | env variables list | _listed_ |
| `Dockerfile` | containerisation | _listed_ |
| `docker-compose.*.yml` | services | _listed_ |
| `src/**/*.py` modules | module list | _listed_ |
| `project/analysis.toon.yaml` | static code analysis (CC, pipelines) | `markpact:file` |
| `project/project.toon.yaml` | project topology | `markpact:file` |
| `project/evolution.toon.yaml` | commit evolution | `markpact:file` |
| `project/map.toon.yaml` | module inventory, function signatures, CC metrics | `markpact:file` |
| `project/duplication.toon.yaml` | code duplication report | `markpact:file` |
| `project/validation.toon.yaml` | vallm validation results | `markpact:file` |
| `project/compact_flow.mmd` | compact call flow diagram | `markpact:file` |
| `project/calls.mmd` | full call graph | `markpact:file` |
| `project/flow.mmd` | execution flow | `markpact:file` |
| `project/context.md` | architecture analysis (code2llm) | _inline markdown_ |
| `project/README.md` | analysis readme | _inline markdown_ |
| `project/prompt.txt` | code2llm prompt used | `markpact:file` |

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

## License

Licensed under Apache-2.0.
