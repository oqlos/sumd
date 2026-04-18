# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Metadata

- **name**: `sumd`
- **version**: `0.1.12`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, app.doql.less, app.doql.css, goal.yaml, .env.example, src(4 mod)

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`, `app.doql.css`)

```less
app {
  name: sumd;
  version: 0.1.11;
}
```

### DOQL Interfaces

- `interface[type="cli"]` — framework: click
- `interface[type="cli"]` page=`sumd` — 
- `interface[type="cli"]` — framework: click
- `interface[type="cli"]` page=`sumd` — 

### Source Modules

- `sumd.cli`
- `sumd.generator`
- `sumd.mcp_server`
- `sumd.parser`

## Interfaces

### CLI Entry Points

- `sumd`
- `sumd-mcp`

## Workflows

### DOQL Workflows (`app.doql.less`, `app.doql.css`)

- **install** `[manual]`: `pip install -e .[dev]`
- **quality** `[manual]`: `pyqual run`
- **quality:fix** `[manual]`: `pyqual run --fix`
- **quality:report** `[manual]`: `pyqual report`
- **test** `[manual]`: `pytest -q`
- **lint** `[manual]`: `ruff check .`
- **fmt** `[manual]`: `ruff format .`
- **build** `[manual]`: `python -m build`
- **clean** `[manual]`: `rm -rf build/ dist/ *.egg-info`
- **structure** `[manual]`: `*(no steps)*`
- **doql:adopt** `[manual]`: `*(no steps)*`
- **doql:export** `[manual]`: `if [ ! -f "app.doql.css" ]`
- **doql:validate** `[manual]`: `*(no steps)*`
- **doql:doctor** `[manual]`: `*(no steps)*`
- **doql:build** `[manual]`: `*(no steps)*`
- **docs:build** `[manual]`: `echo "Building SUMD documentation..." → python -m sumd.cli docs/ docs/`
- **help** `[manual]`: `task --list`
- **install** `["manual"]`: `pip install -e .[dev]`
- **quality** `["manual"]`: `pyqual run`
- **quality:fix** `["manual"]`: `pyqual run --fix`
- **quality:report** `["manual"]`: `pyqual report`
- **test** `["manual"]`: `pytest -q`
- **lint** `["manual"]`: `ruff check .`
- **fmt** `["manual"]`: `ruff format .`
- **build** `["manual"]`: `python -m build`
- **clean** `["manual"]`: `rm -rf build/ dist/ *.egg-info`
- **structure** `["manual"]`: `*(no steps)*`
- **doql:adopt** `["manual"]`: `*(no steps)*`
- **doql:export** `["manual"]`: `if [ ! -f "app.doql.css" ]`
- **doql:validate** `["manual"]`: `*(no steps)*`
- **doql:doctor** `["manual"]`: `*(no steps)*`
- **doql:build** `["manual"]`: `*(no steps)*`
- **docs:build** `["manual"]`: `echo "Building SUMD documentation..." → python -m sumd.cli docs/ docs/`
- **help** `["manual"]`: `task --list`

### Taskfile Tasks (`Taskfile.yml`)

```yaml
tasks:
  install:
    desc: "Install Python dependencies (editable)"
    cmds:
      - pip install -e .[dev]
  quality:
    desc: "Run pyqual quality pipeline"
    cmds:
      - pyqual run
  quality:fix:
    desc: "Run pyqual with auto-fix"
    cmds:
      - pyqual run --fix
  quality:report:
    desc: "Generate pyqual quality report"
    cmds:
      - pyqual report
  test:
    desc: "Run pytest suite"
    cmds:
      - pytest -q
  lint:
    desc: "Run ruff lint check"
    cmds:
      - ruff check .
  fmt:
    desc: "Auto-format with ruff"
    cmds:
      - ruff format .
  build:
    desc: "Build wheel + sdist"
    cmds:
      - python -m build
  clean:
    desc: "Remove build artefacts"
    cmds:
      - rm -rf build/ dist/ *.egg-info
  all:
    desc: "Run install, quality check"
  structure:
    desc: "Generate project structure (app.doql.css + app.doql.less)"
    cmds:
      - echo "📁 Analyzing sumd project structure..."
{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
{{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}"
  doql:adopt:
    desc: "Reverse-engineer sumd project structure (CSS only)"
    cmds:
      - {{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force
  doql:export:
    desc: "Export to LESS format"
    cmds:
      - if [ ! -f "app.doql.css" ]; then
  echo "❌ app.doql.css not found. Run: task structure"
  exit 1
fi
  doql:validate:
    desc: "Validate app.doql.less syntax"
    cmds:
      - if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi
  doql:doctor:
    desc: "Run doql health checks"
    cmds:
      - {{.DOQL_CMD}} doctor
  doql:build:
    desc: "Generate code from app.doql.less"
    cmds:
      - if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi
  analyze:
    desc: "Full doql analysis (structure + validate + doctor)"
  docs:build:
    desc: "Build documentation"
    cmds:
      - echo "Building SUMD documentation..."
  help:
    desc: "Show available tasks"
    cmds:
      - task --list
```

## Configuration

```yaml
project:
  name: sumd
  version: 0.1.12
  env: local
```

## Dependencies

### Runtime

- `click>=8.0`
- `pyyaml>=6.0`
- `toml>=0.10.0`

## Deployment

```bash
pip install sumd

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true         # true = apply fixes without asking` | Behavior |
| `PFIX_AUTO_INSTALL_DEPS` | `true   # true = auto pip/uv install` |  |
| `PFIX_AUTO_RESTART` | `false        # true = os.execv restart after fix` |  |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false         # true = auto-commit fixes` | Git integration |
| `PFIX_GIT_PREFIX` | `pfix:         # commit message prefix` |  |
| `PFIX_CREATE_BACKUPS` | `false     # false = disable .pfix_backups/ directory` | Backup |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`statement`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `sumd/__init__.py:__version__`
