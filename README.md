# SUMD

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.31-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$7.50-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-32.1h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $7.5000 (81 commits)
- 👤 **Human dev:** ~$3211 (32.1h @ $100/h, 30min dedup)

Generated on 2026-05-02 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

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
pip install sumd==0.3.45           # specific version
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

# DSL (Domain Specific Language) operations
sumd dsl                                     # start interactive DSL shell
sumd dsl -c "scan('.')"                      # execute single DSL command
sumd dsl -s script.dsl                       # execute DSL script file
sumd dsl -d /path/to/project                 # set working directory

# CQRS ES (Command Query) operations
sumd cqrs create_sumd_document ./SUMD.md --data '{"project_name":"MyProject"}'
sumd cqrs add_section ./SUMD.md --data '{"section_name":"Architecture","content":"..."}'
sumd cqrs validate_sumd_document ./SUMD.md
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

## File Filtering

SUMD respects standard ignore files to exclude unwanted files and directories from analysis:

### Supported Ignore Files

- **`.gitignore`** - Standard Git ignore patterns (automatically detected)
- **`.sumdignore`** - SUMD-specific ignore patterns (overrides .gitignore)

### Pattern Syntax

Supports full gitignore pattern syntax:

```gitignore
# File patterns
*.log
*.tmp
coverage.xml

# Directory patterns  
temp/
build/
__pycache__/

# Negation (include despite other patterns)
!important.log
!src/temp/
```

### Behavior

- Patterns are read from both `.gitignore` and `.sumdignore` files
- `.sumdignore` patterns take precedence over `.gitignore` patterns
- Improves performance by skipping ignored files during analysis
- Works with all `sumd scan`, `sumd map`, and `sumd analyze` commands

## CQRS ES Architecture

SUMD now implements **Command Query Responsibility Segregation (CQRS)** with **Event Sourcing (ES)** for robust state management and audit trails:

### Architecture Components

- **Commands**: Write operations that modify system state
- **Queries**: Read operations that retrieve system state
- **Events**: Immutable records of state changes
- **Aggregates**: Consistency boundaries for business logic
- **Event Store**: Persistent storage for event history

### Benefits

- **Audit Trail**: Complete history of all changes
- **Temporal Queries**: Reconstruct state at any point in time
- **Scalability**: Separate read/write models
- **Resilience**: Event replay for error recovery

### CLI Integration

```bash
# Execute CQRS commands
sumd cqrs create_sumd_document ./SUMD.md --data '{"project_name":"MyProject"}'
sumd cqrs add_section ./SUMD.md --data '{"section_name":"Architecture","content":"..."}'

# Query system state
sumd cqrs get_aggregate ./SUMD.md
sumd cqrs get_events ./SUMD.md
```

### MCP Integration

The MCP server exposes CQRS ES tools:

- `execute_command` - Execute write commands
- `execute_query` - Execute read queries  
- `get_events` - Retrieve event history
- `get_aggregate` - Get current aggregate state

## DSL (Domain Specific Language)

SUMD provides a powerful DSL for interactive operations and scripting:

### DSL Shell

```bash
# Start interactive shell
sumd dsl

# Execute single command
sumd dsl -c "scan('.') | validate('.')"

# Execute script file
sumd dsl -s script.dsl
```

### DSL Features

- **Arithmetic**: `1 + 2 * 3`
- **Logic**: `x and y or not z`
- **Comparison**: `x == 42`, `name contains "test"`
- **Variables**: `x = 42`, `result = scan('.')`
- **Functions**: `len("hello")`, `exists("file.txt")`
- **Pipelines**: `scan('.') | validate('.') | export("json")`
- **File Operations**: `cat("file.txt")`, `ls("*.md")`, `edit("file.txt", "content")`

### Built-in Commands

#### File Operations
- `cat` - Display file contents
- `ls` - List directory contents  
- `edit` - Edit file content
- `mkdir` - Create directory
- `rm` - Remove file/directory

#### SUMD Operations
- `sumd_scan` - Scan and generate SUMD
- `sumd_map` - Generate project map
- `sumd_validate` - Validate SUMD document
- `sumd_info` - Show document info

#### Search Operations
- `find` - Find files matching pattern
- `grep` - Search text in files

#### Utility Operations
- `echo` - Display message
- `pwd` - Print working directory
- `cd` - Change directory
- `help` - Show help

#### Variables
- `set` - Set variable
- `get` - Get variable value
- `unset` - Remove variable
- `vars` - List all variables

### DSL Examples

```bash
# Basic arithmetic
result = 1 + 2 * 3

# File operations
if exists("SUMD.md"):
    content = cat("SUMD.md")
    print(len(content))

# SUMD workflow
scan(".") | validate(".") | export("json")

# Variable usage
project = "my-project"
files = ls("*.py")
print(f"Found {len(files)} Python files in {project}")

# Conditional logic
if exists("pyproject.toml"):
    scan(".")
    validate("SUMD.md")
else:
    print("No Python project found")
```

### MCP DSL Integration

The MCP server provides DSL tools:

- `execute_dsl` - Execute DSL expressions
- `dsl_shell_info` - Get shell capabilities

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

SUMD is part of a four-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│                     SUMD (opis)                             │
│              Structured Unified Markdown Descriptor         │
│         Project description, intent, architecture           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOQL (wykonanie)                         │
│              Declarative Object Query Language              │
│              Data manipulation and execution                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Taskfile (runtime)                         │
│              Task runner and workflow execution             │
│              Automation and orchestration                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   testql (weryfikacja)                      │
│              Test generation and execution                  │
│              API, GUI, hardware, shell, WebSocket tests     │
└─────────────────────────────────────────────────────────────┘
```

- **SUMD → opis (description)**: Defines what the system is and how it should work
- **DOQL → wykonanie (execution)**: Provides the language to manipulate and execute operations
- **Taskfile → runtime**: Manages the actual execution of workflows and tasks
- **testql → weryfikacja (verification)**: Generates and executes tests across multiple domains

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

## testql Integration

testql is the testing framework in the SUMD ecosystem, providing automated test generation and execution for APIs, GUI, hardware, shell commands, and WebSockets.

### testql Features

#### Test Generation

testql automatically generates test scenarios from various sources:

- **API Tests**: From OpenAPI/Swagger specifications, FastAPI/Flask/Django routes, Express.js endpoints
- **GUI Tests**: From Playwright/Selenium configurations
- **Hardware Tests**: From hardware peripheral configurations
- **Shell Tests**: From CLI command definitions
- **WebSocket Tests**: From WebSocket endpoint definitions
- **Pytest Conversion**: Converts existing Python pytest tests to testql format
- **OQL/CQL Scenarios**: Converts OQL/CQL scenario files to testql format

#### Test Execution

testql executes test scenarios written in `.testql.toon.yaml` format with support for:

- **API Commands**: `API[method, endpoint, expected_status]` with retry logic
- **Assertions**: `ASSERT_STATUS`, `ASSERT_OK`, `ASSERT_CONTAINS`, `ASSERT_JSON`, `ASSERT_HEADERS`, `ASSERT_SCHEMA`, `ASSERT_COOKIES`
- **GUI Commands**: `GUI_START`, `GUI_CLICK`, `GUI_INPUT`, `GUI_ASSERT_VISIBLE`, `GUI_ASSERT_TEXT`, `GUI_CAPTURE`, `GUI_STOP`
- **Hardware Commands**: `ENCODER_ON`, `ENCODER_OFF`, `ENCODER_SCROLL`, `ENCODER_CLICK`, `ENCODER_FOCUS`, `ENCODER_STATUS`
- **Shell Commands**: `SHELL`, `EXEC`, `RUN` with exit code and output assertions
- **WebSocket Commands**: `WS_CONNECT`, `WS_SEND`, `WS_RECEIVE`, `WS_ASSERT_MSG`, `WS_CLOSE`
- **Flow Control**: `WAIT`, `WAIT_FOR`, `LOG`, `PRINT`, `INCLUDE`

#### Endpoint Detection

testql includes automatic endpoint detection from:

- **Docker Compose**: Service port mappings and configurations
- **Kubernetes Configs**: Service and deployment configurations
- **.env Files**: Environment variables with URL, HOST, PORT patterns
- **config.py Files**: Python configuration files with host/port/url assignments
- **Framework Detectors**: FastAPI, Flask, Django, Express.js route discovery
- **Specification Files**: OpenAPI/Swagger, GraphQL schemas

#### Configuration

testql scenarios support configuration via `CONFIG` block:

```yaml
CONFIG[4]{key, value}:
  base_url, ${api_url:-http://localhost:8100}
  timeout_ms, 10000
  retry_count, 3
  retry_backoff_ms, 100
```

#### Reporting

testql generates HTML reports from test results:

```bash
# Generate report from pytest JSON output
pytest --json-report --json-report-file=test-results.json
testql report test-results.json -o report.html

# Generate example report
testql report --example -o report.html
```

#### Integration with SUMD

SUMD automatically embeds testql scenarios from `testql-scenarios/` directory into SUMD.md:

```yaml markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -msumd
  timeout_ms, 10000

LOG[3]{message}:
  "Test CLI help command"
  "Test CLI version command"
  "Test CLI main workflow"
```

#### Workflow Integration

testql is integrated into SUMD workflows:

```bash
# Run pytest with testql report generation
task test:report

# Generate testql scenario scaffolds from OpenAPI
sumd scaffold ./my-project --type smoke
sumd scaffold ./my-project --type crud
```

## License

Licensed under Apache-2.0.
