# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `sumd`
- **version**: `0.3.34`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, src(10 mod), project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: sumd;
  version: 0.3.34;
}

dependencies {
  runtime: "click>=8.3.3, pyyaml>=6.0.3, toml>=0.10.2, goal>=2.1.190, costs>=0.1.50, pfix>=0.1.72";
  dev: "pytest>=9.0.3, pytest-cov>=7.1.0, ruff>=0.15.11, build>=1.4.4, twine>=6.2.0, pyqual>=0.1.143, goal>=2.1.190, costs>=0.1.50, pfix>=0.1.72, mcp>=1.27.0";
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="sumd"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PIP}} install -e .[dev];
}

workflow[name="deps:update"] {
  trigger: manual;
  step-1: run cmd=PIP="{{.VENV_PIP}}"
$PIP install --upgrade pip
OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
if [ -z "$OUTDATED" ]; then
  echo "✅ All packages are up to date."
else
  echo "📦 Upgrading: $OUTDATED"
  echo "$OUTDATED" | xargs $PIP install --upgrade
  echo "✅ Done."
fi;
}

workflow[name="quality"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual run;
}

workflow[name="quality:fix"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual report;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pytest -q;
}

workflow[name="test:report"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pytest --json-report --json-report-file=test-results.json -q;
  step-2: run cmd={{.VENV_PY}} -m testql report test-results.json -o report.html;
}

workflow[name="test:report:example"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m testql report --example -o report.html;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=ruff check .;
}

workflow[name="fmt"] {
  trigger: manual;
  step-1: run cmd=ruff format .;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m build;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: manual;
  step-1: run cmd=echo "📁 Analyzing sumd project structure..."
{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force
echo "✅ Structure generated: {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: manual;
  step-1: run cmd={{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force;
  step-2: run cmd=echo "✅ Captured in app.doql.less";
}

workflow[name="doql:export"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "app.doql.less" ]; then
  echo "❌ app.doql.less not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} validate;
}

workflow[name="doql:doctor"] {
  trigger: manual;
  step-1: run cmd={{.DOQL_CMD}} doctor;
}

workflow[name="doql:build"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} build app.doql.less --out build/;
}

workflow[name="docs:build"] {
  trigger: manual;
  step-1: run cmd=echo "Building SUMD documentation...";
  step-2: run cmd={{.VENV_PY}} -m sumd.cli docs/ docs/;
}

workflow[name="sumd"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m sumd.cli scan .;
}

workflow[name="sumr"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m sumd.cli scan . --profile refactor;
}

workflow[name="version:bump"] {
  trigger: manual;
  step-1: run cmd=hatch version patch;
  step-2: run cmd=echo "✅ Version bumped:";
  step-3: run cmd=hatch version;
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m twine upload dist/*;
}

workflow[name="doctor"] {
  trigger: manual;
  step-1: run cmd=echo "=== sumd doctor ==="
check() { "$@" > /dev/null 2>&1 && echo "  ✅ $1" || echo "  ❌ $1  (command failed: $*)"; }
check {{.VENV_PY}} -m pyqual doctor
check {{.VENV_PY}} -m pytest --version
check ruff --version
check {{.PWD}}/.venv/bin/sumd --version
check {{.PWD}}/.venv/bin/sumd --help
echo "=== done ===";
}

workflow[name="help"] {
  trigger: manual;
  step-1: run cmd=task --list;
}

workflow[name="analyze"] {
  trigger: manual;
  step-1: run cmd=echo "🔬 Running project analysis...";
  step-2: run cmd=sumd analyze . --tools code2llm,redup,vallm;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
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

## Interfaces

### CLI Entry Points

- `sumd`
- `sumr`
- `sumd-mcp`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m sumd
  timeout_ms, 10000

LOG[3]{message}:
  "Test CLI help command"
  "Test CLI version command"
  "Test CLI main workflow"
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

LOG[8]{message}:
  "Test: TestExtractEnv_test_captures_inline_comment"
  "Test: TestExtractRequirements_test_parses_requirements_txt"
  "Test: test_captures_inline_comment"
  "Test: test_parses_requirements_txt"
  "Test: TestExtractEnv_test_captures_inline_comment"
  "Test: TestExtractRequirements_test_parses_requirements_txt"
  "Test: test_captures_inline_comment"
  "Test: test_parses_requirements_txt"
```

#### `testql-scenarios/smoke-generic.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/smoke-generic.testql.toon.yaml
# SCENARIO: smoke-generic.testql.toon.yaml — smoke tests for sumd CLI
# TYPE: smoke
# VERSION: 1.0

# ── Konfiguracja ──────────────────────────────────────
CONFIG[2]{key, value}:
  base_path, /api/v1
  timeout_ms, 5000

# ── Wywołania API ─────────────────────────────────────
API[2]{method, endpoint, status}:
  GET, /health, 200
  GET, /, 200

# ── Asercje ───────────────────────────────────────────
ASSERT[2]{field, operator, expected}:
  status, <, 500
  content_type, contains, application/json
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
# Taskfile.yml — sumd (Structured Unified Markdown Descriptor) project runner
# https://taskfile.dev

version: "3"

vars:
  APP_NAME: sumd
  DOQL_OUTPUT: app.doql.less
  DOQL_CMD: "{{if eq OS \"windows\"}}doql.exe{{else}}doql{{end}}"
  VENV_PY: "{{.PWD}}/.venv/bin/python"
  VENV_PIP: "{{.PWD}}/.venv/bin/pip"

env:
  PYTHONPATH: "{{.PWD}}"

tasks:
  # ─────────────────────────────────────────────────────────────────────────────
  # Development
  # ─────────────────────────────────────────────────────────────────────────────

  install:
    desc: Install Python dependencies (editable)
    cmds:
      - "{{.VENV_PIP}} install -e .[dev]"

  deps:update:
    desc: Upgrade all outdated Python packages in the project venv
    cmds:
      - |
        PIP="{{.VENV_PIP}}"
        $PIP install --upgrade pip
        OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
        if [ -z "$OUTDATED" ]; then
          echo "✅ All packages are up to date."
        else
          echo "📦 Upgrading: $OUTDATED"
          echo "$OUTDATED" | xargs $PIP install --upgrade
          echo "✅ Done."
        fi

  quality:
    desc: Run pyqual quality pipeline (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual run"

  quality:fix:
    desc: Run pyqual with auto-fix (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual run --fix"

  quality:report:
    desc: Generate pyqual quality report (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual report"

  test:
    desc: Run pytest suite
    cmds:
      - "{{.VENV_PY}} -m pytest -q"

  test:report:
    desc: Run pytest suite and generate HTML report
    cmds:
      - "{{.VENV_PY}} -m pytest --json-report --json-report-file=test-results.json -q"
      - "{{.VENV_PY}} -m testql report test-results.json -o report.html"

  test:report:example:
    desc: Generate example testql HTML report
    cmds:
      - "{{.VENV_PY}} -m testql report --example -o report.html"

  lint:
    desc: Run ruff lint check
    cmds:
      - ruff check .

  fmt:
    desc: Auto-format with ruff
    cmds:
      - ruff format .

  build:
    desc: Build wheel + sdist
    cmds:
      - "{{.VENV_PY}} -m build"

  clean:
    desc: Remove build artefacts
    cmds:
      - rm -rf build/ dist/ *.egg-info

  all:
    desc: Run install, quality check
    cmds:
      - task: install
      - task: quality

  # ─────────────────────────────────────────────────────────────────────────────
  # Doql Integration
  # ─────────────────────────────────────────────────────────────────────────────

  structure:
    desc: Generate project structure (app.doql.less)
    cmds:
      - |
        echo "📁 Analyzing sumd project structure..."
        {{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force
        echo "✅ Structure generated: {{.DOQL_OUTPUT}}"

  doql:adopt:
    desc: Reverse-engineer sumd project structure (LESS format)
    cmds:
      - "{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force"
      - echo "✅ Captured in app.doql.less"

  doql:export:
    desc: Export app.doql.less to other formats
    cmds:
      - |
        if [ ! -f "app.doql.less" ]; then
          echo "❌ app.doql.less not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}"
      - echo "✅ Exported to {{.DOQL_OUTPUT}}"

  doql:validate:
    desc: Validate app.doql.less syntax
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} validate"

  doql:doctor:
    desc: Run doql health checks
    cmds:
      - "{{.DOQL_CMD}} doctor"

  doql:build:
    desc: Generate code from app.doql.less
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} build app.doql.less --out build/"

  analyze:
    desc: Full doql analysis (structure + validate + doctor)
    cmds:
      - task: structure
      - task: doql:validate
      - task: doql:doctor

  # ─────────────────────────────────────────────────────────────────────────────
  # Documentation
  # ─────────────────────────────────────────────────────────────────────────────

  docs:build:
    desc: Build documentation
    cmds:
      - echo "Building SUMD documentation..."
      - "{{.VENV_PY}} -m sumd.cli docs/ docs/"

  # ─────────────────────────────────────────────────────────────────────────────
  # SUMD Documentation Generation
  # ─────────────────────────────────────────────────────────────────────────────

  sumd:
    desc: Generate SUMD.md (full project documentation)
    cmds:
      - "{{.VENV_PY}} -m sumd.cli scan ."

  sumr:
    desc: Generate SUMR.md (pre-refactoring analysis report)
    cmds:
      - "{{.VENV_PY}} -m sumd.cli scan . --profile refactor"

  # ─────────────────────────────────────────────────────────────────────────────
  # Release
  # ─────────────────────────────────────────────────────────────────────────────

  version:bump:
    desc: Bump patch version (hatch)
    cmds:
      - hatch version patch
      - echo "✅ Version bumped:"
      - hatch version

  publish:
    desc: Build and publish to PyPI
    cmds:
      - task: clean
      - task: build
      - "{{.VENV_PY}} -m twine upload dist/*"

  # ─────────────────────────────────────────────────────────────────────────────
  # Utility
  # ─────────────────────────────────────────────────────────────────────────────

  check:
    desc: Full pre-commit check (lint + test + quality)
    cmds:
      - task: lint
      - task: test
      - task: quality

  doctor:
    desc: Smoke-test all external CLI tools used by this project
    cmds:
      - |
        echo "=== sumd doctor ==="
        check() { "$@" > /dev/null 2>&1 && echo "  ✅ $1" || echo "  ❌ $1  (command failed: $*)"; }
        check {{.VENV_PY}} -m pyqual doctor
        check {{.VENV_PY}} -m pytest --version
        check ruff --version
        check {{.PWD}}/.venv/bin/sumd --version
        check {{.PWD}}/.venv/bin/sumd --help
        echo "=== done ==="

  help:
    desc: Show available tasks
    cmds:
      - task --list

  all:
    desc: Install, full check, generate SUMD docs
    cmds:
      - task: install
      - task: check
      - task: sumd
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: quality-loop

  # Quickstart: replace all of this with a single profile line:
  #   profile: python-minimal   # analyze → validate → lint → fix → test
  #   profile: python-publish   # + git-push and make-publish
  #   profile: python-secure    # + pip-audit, bandit, detect-secrets
  #   profile: python           # standard (needs manual stage config)
  #   profile: ci               # CI-only, no fix
  # See: pyqual profiles

  # Quality gates — pipeline iterates until ALL pass
  metrics:
    cc_max: 15           # cyclomatic complexity per function
    vallm_pass_min: 60   # vallm validation pass rate (%)
    coverage_min: 35     # branch+statement coverage (%) — 37% measured with --cov-branch

  # Pipeline stages — use 'tool:' for built-in presets or 'run:' for custom commands
  # See all presets: pyqual tools
  # when: any_stage_fail    — run only when a prior stage in this iteration failed
  # when: metrics_fail      — run only when quality gates are not yet passing
  # when: first_iteration   — run only on iteration 1 (skip re-runs after fix)
  # when: after_fix         — run only after the fix stage ran in this iteration
  stages:
    - name: analyze
      tool: code2llm-filtered   # uses sensible exclude defaults

    - name: validate
      tool: vallm-filtered      # uses sensible exclude defaults

    - name: prefact
      tool: prefact
      optional: true
      when: any_stage_fail
      timeout: 900

    - name: fix
      tool: llx-fix
      optional: true
      when: any_stage_fail
      timeout: 1800

    - name: test
      tool: pytest

    - name: push
      tool: git-push            # built-in: git add + commit + push
      optional: true
      timeout: 120

    - name: publish
      tool: twine-publish       # built-in: python -m build + twine upload
      optional: true
      when: metrics_pass
      timeout: 120

  # Loop behavior
  loop:
    max_iterations: 3
    on_fail: report      # report | create_ticket | block
    ticket_backends:     # backends to sync when on_fail = create_ticket
      - markdown        # TODO.md (default)
      # - github        # GitHub Issues (requires GITHUB_TOKEN)

  # Environment (optional)
  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Configuration

```yaml
project:
  name: sumd
  version: 0.3.34
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
click>=8.3.3
pyyaml>=6.0.3
toml>=0.10.2
goal>=2.1.190
costs>=0.1.50
pfix>=0.1.72
```

### Development

```text markpact:deps python scope=dev
pytest>=9.0.3
pytest-cov>=7.1.0
ruff>=0.15.11
build>=1.4.4
twine>=6.2.0
pyqual>=0.1.143
goal>=2.1.190
costs>=0.1.50
pfix>=0.1.72
mcp>=1.27.0
```

## Deployment

```bash markpact:run
pip install sumd

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`statement`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `sumd/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# sumd | 47f 8263L | python:40,shell:5,less:2 | 2026-04-23
# stats: 223 func | 63 cls | 47 mod | CC̄=4.5 | critical:10 | cycles:0
# alerts[5]: CC _map_cc_stats=12; CC run=11; CC analyze=11; CC _render_api_stubs=11; CC _walk_projects=10
# hotspots[5]: scan fan=18; scaffold fan=18; analyze fan=17; generate fan=15; _parse_doql_content fan=14
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[47]:
  app.doql.less,196
  examples/app.doql.less,60
  examples/basic/demo.sh,50
  examples/llm/anthropic_example.py,61
  examples/llm/llm_cli_example.sh,37
  examples/llm/ollama_example.sh,38
  examples/llm/openai_example.py,89
  examples/mcp/mcp_client.py,139
  project.sh,41
  scripts/bootstrap.sh,70
  sumd/__init__.py,36
  sumd/cli.py,1683
  sumd/extractor.py,909
  sumd/generator.py,16
  sumd/mcp_server.py,359
  sumd/models.py,46
  sumd/parser.py,196
  sumd/pipeline.py,436
  sumd/renderer.py,30
  sumd/sections/__init__.py,104
  sumd/sections/api_stubs.py,77
  sumd/sections/architecture.py,157
  sumd/sections/base.py,94
  sumd/sections/call_graph.py,157
  sumd/sections/code_analysis.py,69
  sumd/sections/configuration.py,45
  sumd/sections/dependencies.py,98
  sumd/sections/deployment.py,112
  sumd/sections/environment.py,73
  sumd/sections/extras.py,73
  sumd/sections/interfaces.py,158
  sumd/sections/metadata.py,52
  sumd/sections/quality.py,83
  sumd/sections/refactor_analysis.py,69
  sumd/sections/source_snippets.py,70
  sumd/sections/test_contracts.py,79
  sumd/sections/workflows.py,87
  sumd/toon_parser.py,174
  sumd/validator.py,330
  tests/test_cli.py,324
  tests/test_dogfood.py,148
  tests/test_extractor.py,313
  tests/test_mcp_server.py,234
  tests/test_parser.py,145
  tests/test_pipeline.py,136
  tests/test_sections.py,298
  tests/test_statement.py,12
D:
  examples/llm/anthropic_example.py:
    e: ask,main
    ask(sumd_path;question;model)
    main()
  examples/llm/openai_example.py:
    e: build_context,ask,main
    build_context(sumd_path)
    ask(sumd_path;question;model)
    main()
  examples/mcp/mcp_client.py:
    e: run,main
    run(sumd_file;single_tool;tool_args)
    main()
  sumd/__init__.py:
  sumd/cli.py:
    e: _detect_project_type,_render_doql_boilerplate,_node_framework,_node_spec_from_package_json,_build_doql_spec,_generate_doql_less,cli,validate,export,info,generate,extract,_is_project_dir,_walk_projects,_detect_projects,_ensure_venv,_tool_bin,_run_one_tool,_run_analysis_tools,_export_sumd_json,_render_write_validate,_echo_scan_result,_maybe_generate_doql,_finalize_scan,_scan_one_project,scan,lint,_lint_collect_paths,_lint_print_result,_setup_tools_venv,_run_code2llm_formats,_run_tool_subprocess,analyze,_api_scenario_template,_scaffold_write,_scaffold_smoke_scenario,_scaffold_crud_scenarios,_scaffold_from_openapi,_scaffold_generic,scaffold,map_cmd,main,main_sumr
    _detect_project_type(proj_dir)
    _render_doql_boilerplate(project_name;spec;extra_workflows)
    _node_framework(deps)
    _node_spec_from_package_json(pkg_json)
    _build_doql_spec(proj_dir;project_type)
    _generate_doql_less(proj_dir;project_name;version;force;project_type)
    cli()
    validate(file)
    export(file;format;output)
    info(file)
    generate(file;format;output)
    extract(file;section)
    _is_project_dir(d)
    _walk_projects(path;projects;max_depth;depth)
    _detect_projects(workspace;max_depth)
    _ensure_venv(tools_dir;venv_dir;tool_list)
    _tool_bin(bin_dir;name)
    _run_one_tool(tool;bin_dir;proj_dir;project_output)
    _run_analysis_tools(proj_dir;tool_list;skip_tools)
    _export_sumd_json(proj_dir;doc)
    _render_write_validate(proj_dir;sumd_path;raw;profile)
    _echo_scan_result(proj_dir;doc;sources;cb_warnings)
    _maybe_generate_doql(proj_dir;fix)
    _finalize_scan(proj_dir;doc;sources;cb_warnings;export_json;run_analyze;tool_list;doql_sync;sumd_path)
    _scan_one_project(proj_dir;fix;raw;export_json;run_analyze;tool_list;parser_inst;profile;generate_doql;doql_sync)
    scan(workspace;export_json;report;fix;raw;analyze;tools;profile;depth;generate_doql;doql_sync)
    lint(files;workspace;as_json)
    _lint_collect_paths(files;workspace)
    _lint_print_result(path;r)
    _setup_tools_venv(venv_dir;tool_list;force)
    _run_code2llm_formats(bin_dir;project;project_output)
    _run_tool_subprocess(bin_dir;tool;cmd_args)
    analyze(project;tools;force)
    _api_scenario_template(name;scenario_type;endpoints_block;base_path)
    _scaffold_write(path;content;force;generated;skipped)
    _scaffold_smoke_scenario(paths;base;out_dir;force;generated;skipped)
    _scaffold_crud_scenarios(groups;base;out_dir;force;generated;skipped)
    _scaffold_from_openapi(spec;out_dir;scenario_type;force;generated;skipped)
    _scaffold_generic(out_dir;force;generated;skipped)
    scaffold(project;output;force;scenario_type)
    map_cmd(project;output;force;stdout)
    main()
    main_sumr()
  sumd/extractor.py:
    e: _read_toml,extract_pyproject,_first_task_cmd,extract_taskfile,_parse_openapi_endpoints,extract_openapi,_parse_doql_entities,_parse_doql_interfaces,_parse_doql_workflows,_parse_doql_content,extract_doql,extract_pyqual,extract_python_modules,extract_readme_title,extract_requirements,extract_makefile,extract_goal,extract_env,_parse_dockerfile_line,extract_dockerfile,extract_docker_compose,extract_package_json,_lang_of,_fan_out,_cc_estimate,_try_radon_cc,_analyse_py_top_funcs,_analyse_class_methods,_analyse_py_top_classes,_analyse_py_module,_is_map_ignored_path,_collect_map_files,_render_map_detail,_map_cc_stats,_render_py_module_detail,generate_map_toon,required_tools_for_profile,extract_source_snippets,extract_project_analysis
    _read_toml(path)
    extract_pyproject(proj_dir)
    _first_task_cmd(cmds)
    extract_taskfile(proj_dir)
    _parse_openapi_endpoints(paths)
    extract_openapi(proj_dir)
    _parse_doql_entities(content)
    _parse_doql_interfaces(content)
    _parse_doql_workflows(content)
    _parse_doql_content(content)
    extract_doql(proj_dir)
    extract_pyqual(proj_dir)
    extract_python_modules(proj_dir;pkg_name)
    extract_readme_title(proj_dir)
    extract_requirements(proj_dir)
    extract_makefile(proj_dir)
    extract_goal(proj_dir)
    extract_env(proj_dir)
    _parse_dockerfile_line(line;parsed)
    extract_dockerfile(proj_dir)
    extract_docker_compose(proj_dir)
    extract_package_json(proj_dir)
    _lang_of(path)
    _fan_out(func_node)
    _cc_estimate(func_node)
    _try_radon_cc(src)
    _analyse_py_top_funcs(tree;radon_cc)
    _analyse_class_methods(node;radon_cc)
    _analyse_py_top_classes(tree;radon_cc)
    _analyse_py_module(path)
    _is_map_ignored_path(p)
    _collect_map_files(proj_dir)
    _render_map_detail(proj_dir;modules)
    _map_cc_stats(all_funcs)
    _render_py_module_detail(rel;info;a)
    generate_map_toon(proj_dir)
    required_tools_for_profile(profile)
    extract_source_snippets(proj_dir;pkg_name)
    extract_project_analysis(proj_dir;refactor)
  sumd/generator.py:
  sumd/mcp_server.py:
    e: _doc_to_dict,_resolve_path,list_tools,_tool_parse_sumd,_tool_validate_sumd,_tool_export_sumd,_tool_list_sections,_tool_get_section,_tool_info_sumd,_tool_generate_sumd,call_tool,main
    _doc_to_dict(doc)
    _resolve_path(path)
    list_tools()
    _tool_parse_sumd(arguments)
    _tool_validate_sumd(arguments)
    _tool_export_sumd(arguments)
    _tool_list_sections(arguments)
    _tool_get_section(arguments)
    _tool_info_sumd(arguments)
    _tool_generate_sumd(arguments)
    call_tool(name;arguments)
    main()
  sumd/models.py:
    e: SectionType,Section,SUMDDocument
    SectionType:  # SUMD section types.
    Section:  # Represents a SUMD section.
    SUMDDocument:  # Represents a parsed SUMD document.
  sumd/parser.py:
    e: parse,parse_file,validate,SUMDParser
    SUMDParser: __init__(0),parse(1),parse_file(1),_parse_header(1),_parse_sections(1),validate(1)  # Parser for SUMD markdown documents.
    parse(content)
    parse_file(path)
    validate(document)
  sumd/pipeline.py:
    e: _refresh_map_toon,_find_tools_bin_dir,_run_tool_if_present,_refresh_analysis_files,_collect_tool_sources,_doql_sources,_collect_pkg_sources,_collect_infra_sources,_collect_sources,_inject_toc,RenderPipeline
    RenderPipeline: __init__(2),_collect(0),_build_registered_sections(2),_render_legacy_sections(1),_assemble(2),run(2)  # Collect project data → build sections → render → inject TOC.
    _refresh_map_toon(proj_dir)
    _find_tools_bin_dir(proj_dir)
    _run_tool_if_present(bin_dir;name;args;proj_dir)
    _refresh_analysis_files(proj_dir;profile)
    _collect_tool_sources(pyproj;reqs;tasks;makefile;scenarios)
    _doql_sources(doql)
    _collect_pkg_sources(pyproj;reqs;tasks;makefile;scenarios;openapi;doql;pyqual;goal;env_vars)
    _collect_infra_sources(dockerfile;compose;pkg_json;modules;project_analysis)
    _collect_sources(pyproj;reqs;tasks;makefile;scenarios;openapi;doql;pyqual;goal;env_vars;dockerfile;compose;pkg_json;modules;project_analysis)
    _inject_toc(content)
  sumd/renderer.py:
    e: generate_sumd_content
    generate_sumd_content(proj_dir;return_sources;raw_sources;profile)
  sumd/sections/__init__.py:
  sumd/sections/api_stubs.py:
    e: _render_api_stubs,ApiStubsSection
    ApiStubsSection: should_render(1),render(1)
    _render_api_stubs(openapi)
  sumd/sections/architecture.py:
    e: _render_architecture_doql_section,_render_architecture_modules,_render_doql_app,_render_doql_entities,_render_doql_interfaces,_render_doql_integrations,_render_architecture_doql_parsed,_render_architecture,ArchitectureSection
    ArchitectureSection: should_render(1),render(1)
    _render_architecture_doql_section(doql;proj_dir;raw_sources;L)
    _render_architecture_modules(modules;name;L)
    _render_doql_app(doql;L)
    _render_doql_entities(doql;L)
    _render_doql_interfaces(doql;L)
    _render_doql_integrations(doql;L)
    _render_architecture_doql_parsed(doql;L)
    _render_architecture(doql;modules;name;proj_dir;raw_sources)
  sumd/sections/base.py:
    e: RenderContext,Section
    RenderContext:  # All extracted data for a project, passed to every Section.re
    Section: should_render(1),render(1)  # Protocol for all SUMD section renderers.
  sumd/sections/call_graph.py:
    e: _parse_calls_header,_parse_hub_stat_line,_process_in_hubs_line,_parse_calls_hubs,_parse_calls_toon,_render_call_graph,CallGraphSection
    CallGraphSection: should_render(1),render(1)
    _parse_calls_header(lines)
    _parse_hub_stat_line(line)
    _process_in_hubs_line(line;hubs;current_hub)
    _parse_calls_hubs(lines)
    _parse_calls_toon(content)
    _render_call_graph(project_analysis)
  sumd/sections/code_analysis.py:
    e: _render_code_analysis,CodeAnalysisSection
    CodeAnalysisSection: should_render(1),render(1)
    _render_code_analysis(project_analysis;skip_files)
  sumd/sections/configuration.py:
    e: _render_configuration_section,ConfigurationSection
    ConfigurationSection: should_render(1),render(1)
    _render_configuration_section(name;version)
  sumd/sections/dependencies.py:
    e: _render_deps_runtime,_render_deps_dev,_render_dependencies,DependenciesSection
    DependenciesSection: should_render(1),render(1)
    _render_deps_runtime(deps;node_deps;L)
    _render_deps_dev(dev_deps;node_dev;L)
    _render_dependencies(deps;dev_deps;pkg_json)
  sumd/sections/deployment.py:
    e: _render_deployment_install,_render_deployment_reqs,_render_dockerfile_info,_render_deployment_docker,_render_deployment,DeploymentSection
    DeploymentSection: should_render(1),render(1)
    _render_deployment_install(pkg_json;name;L)
    _render_deployment_reqs(reqs;L)
    _render_dockerfile_info(dockerfile;a)
    _render_deployment_docker(dockerfile;compose;L)
    _render_deployment(pkg_json;name;reqs;dockerfile;compose)
  sumd/sections/environment.py:
    e: _render_env_section,_render_goal_section,EnvironmentSection
    EnvironmentSection: should_render(1),render(1)
    _render_env_section(env_vars)
    _render_goal_section(goal)
  sumd/sections/extras.py:
    e: _render_makefile_targets,_render_pkg_json_scripts,_render_extras,ExtrasSection
    ExtrasSection: should_render(1),render(1)
    _render_makefile_targets(makefile;a)
    _render_pkg_json_scripts(pkg_json;a)
    _render_extras(makefile;pkg_json)
  sumd/sections/interfaces.py:
    e: _render_interfaces_openapi,_render_testql_raw,_render_testql_endpoint,_render_testql_extras,_render_testql_one_structured,_render_interfaces_testql,_render_interfaces,InterfacesSection
    InterfacesSection: should_render(1),render(1)
    _render_interfaces_openapi(openapi;proj_dir;raw_sources;L)
    _render_testql_raw(scenarios;proj_dir;L)
    _render_testql_endpoint(ep;L)
    _render_testql_extras(sc;L)
    _render_testql_one_structured(sc;L)
    _render_interfaces_testql(scenarios;proj_dir;raw_sources;L)
    _render_interfaces(scripts;openapi;scenarios;proj_dir;raw_sources)
  sumd/sections/metadata.py:
    e: MetadataSection
    MetadataSection: should_render(1),render(1)  # Render ## Metadata — always present, all profiles.
  sumd/sections/quality.py:
    e: _render_quality_raw,_render_quality_parsed,_render_quality,QualitySection
    QualitySection: should_render(1),render(1)
    _render_quality_raw(proj_dir;L)
    _render_quality_parsed(pyqual;L)
    _render_quality(pyqual;proj_dir;raw_sources)
  sumd/sections/refactor_analysis.py:
    e: RefactorAnalysisSection
    RefactorAnalysisSection: should_render(1),render(1)
  sumd/sections/source_snippets.py:
    e: _render_source_snippets,SourceSnippetsSection
    SourceSnippetsSection: should_render(1),render(1)
    _render_source_snippets(source_snippets;top_n)
  sumd/sections/test_contracts.py:
    e: _render_scenario_contract,_render_test_contracts,TestContractsSection
    TestContractsSection: should_render(1),render(1)
    _render_scenario_contract(sc;a)
    _render_test_contracts(scenarios)
  sumd/sections/workflows.py:
    e: _render_workflows_doql,_render_workflows_taskfile,_render_workflows,WorkflowsSection
    WorkflowsSection: should_render(1),render(1)
    _render_workflows_doql(doql;L)
    _render_workflows_taskfile(tasks;proj_dir;raw_sources;L)
    _render_workflows(doql;tasks;proj_dir;raw_sources)
  sumd/toon_parser.py:
    e: _parse_toon_block_config,_parse_toon_block_api,_parse_toon_block_assert,_parse_toon_block_performance,_parse_toon_block_navigate,_parse_toon_block_gui,_parse_toon_file,extract_testql_scenarios
    _parse_toon_block_config(lines)
    _parse_toon_block_api(content)
    _parse_toon_block_assert(lines)
    _parse_toon_block_performance(lines)
    _parse_toon_block_navigate(lines)
    _parse_toon_block_gui(lines)
    _parse_toon_file(f)
    extract_testql_scenarios(proj_dir)
  sumd/validator.py:
    e: _validate_yaml_body,_validate_less_css_body,_validate_mermaid_body,_validate_toon_body,_validate_bash_body,_validate_deps_body,_validate_markpact_meta,validate_codeblocks,_check_h1,_check_required_sections,_check_metadata_fields,_check_unclosed_fences,_check_empty_links,validate_markdown,validate_sumd_file,CodeBlockIssue
    CodeBlockIssue:
    _validate_yaml_body(body;path)
    _validate_less_css_body(body;path)
    _validate_mermaid_body(body;path)
    _validate_toon_body(body;path)
    _validate_bash_body(body;path)
    _validate_deps_body(body;path)
    _validate_markpact_meta(mp;line_no;lang;meta;issues)
    validate_codeblocks(content;source)
    _check_h1(lines;source)
    _check_required_sections(lines;source;profile)
    _check_metadata_fields(lines;source)
    _check_unclosed_fences(lines;source)
    _check_empty_links(content;source)
    validate_markdown(content;source;profile)
    validate_sumd_file(path;profile)
  tests/test_cli.py:
    e: sumd_file,TestValidateCommand,TestInfoCommand,TestExportCommand,TestCliVersion,TestCliHelp,TestProjectDetection,TestNodeSpecFromPackageJson,TestGenerateDoqlLess
    TestValidateCommand: test_valid_file_exits_zero(1),test_valid_file_prints_ok(1),test_missing_file_exits_nonzero(1)
    TestInfoCommand: test_info_runs(1)
    TestExportCommand: test_export_json(1),test_export_to_output_file(2),test_export_markdown(1)
    TestCliVersion: test_version_option(0)
    TestCliHelp: test_help(0),test_validate_help(0),test_export_help(0),test_scan_help(0)
    TestProjectDetection: test_is_project_dir_accepts_language_marker(3),test_is_project_dir_accepts_glob_markers(3),test_empty_dir_is_not_project(1),test_detect_projects_finds_mixed_languages(1)  # Detection must work across all supported languages/project t
    TestNodeSpecFromPackageJson: test_framework_detection(2),test_spec_uses_real_scripts_and_extras(0),test_spec_falls_back_without_scripts(0)  # Node DOQL spec must mirror real package.json (scripts + fram
    TestGenerateDoqlLess: _pkg(1),test_fresh_generation_for_node_uses_real_scripts(1),test_force_regenerates_autogen_file_without_duplicating(1),test_force_preserves_user_authored_file(1),test_no_force_skips_existing(1)  # Refresh behaviour for app.doql.less generation.
    sumd_file(tmp_path)
  tests/test_dogfood.py:
    e: _run,project_copy,test_sumd_scans_itself,test_sumd_scans_all_profiles,test_sumr_generates_sumr_md,test_sumd_lint_passes_on_generated_output,test_sumd_version_flag,test_sumd_scan_produces_no_unhandled_exceptions
    _run(cmd;cwd;timeout)
    project_copy(tmp_path_factory)
    test_sumd_scans_itself(project_copy)
    test_sumd_scans_all_profiles(project_copy;profile)
    test_sumr_generates_sumr_md(project_copy)
    test_sumd_lint_passes_on_generated_output(project_copy)
    test_sumd_version_flag()
    test_sumd_scan_produces_no_unhandled_exceptions(project_copy)
  tests/test_extractor.py:
    e: TestExtractPyproject,TestExtractTaskfile,TestExtractPyqual,TestExtractPythonModules,TestExtractReadmeTitle,TestExtractEnv,TestExtractGoal,TestExtractProjectAnalysis,TestExtractRequirements,TestExtractMakefile
    TestExtractPyproject: test_missing_file_returns_empty(1),test_basic_fields(1),test_dependencies_parsed(1),test_dev_dependencies_from_optional(1),test_fallback_name_is_dir_name(1),test_corrupt_toml_returns_empty(1)
    TestExtractTaskfile: test_missing_returns_empty(1),test_parses_tasks(1),test_task_without_desc(1),test_multiple_tasks(1)
    TestExtractPyqual: test_missing_returns_empty(1),test_parses_pipeline(1),test_flat_format(1)
    TestExtractPythonModules: test_missing_pkg_dir_returns_empty(1),test_lists_modules(1),test_excludes_dunder_files(1)
    TestExtractReadmeTitle: test_missing_returns_empty(1),test_extracts_h1(1),test_no_h1_returns_empty(1),test_first_h1_only(1)
    TestExtractEnv: test_missing_returns_empty(1),test_parses_key_value(1),test_captures_preceding_comment(1),test_captures_inline_comment(1),test_empty_value_becomes_not_set(1)
    TestExtractGoal: test_missing_returns_empty(1),test_parses_project_and_versioning(1)
    TestExtractProjectAnalysis: test_missing_project_dir_returns_empty(1),test_loads_calls_toon_yaml(1),test_refactor_mode_loads_extra_files(1),test_missing_files_skipped(1)
    TestExtractRequirements: test_no_requirements_returns_empty(1),test_parses_requirements_txt(1),test_ignores_comments_and_flags(1)
    TestExtractMakefile: test_missing_returns_empty(1),test_parses_targets(1),test_comment_captured(1)
  tests/test_mcp_server.py:
    e: sumd_file,run,TestDocToDict,TestResolvePath,TestListTools,TestParseSumd,TestValidateSumd,TestExportSumd,TestListSections,TestGetSection,TestInfoSumd,TestGenerateSumd,TestUnknownTool
    TestDocToDict: test_has_required_keys(1),test_section_has_fields(1)
    TestResolvePath: test_absolute_path_unchanged(1),test_relative_resolves_from_cwd(0)
    TestListTools: test_returns_seven_tools(0),test_tool_names(0),test_each_tool_has_input_schema(0)
    TestParseSumd: test_returns_json(1),test_missing_file_returns_error(1)
    TestValidateSumd: test_valid_file(1),test_missing_file_returns_error(1)
    TestExportSumd: test_export_json(1),test_export_markdown(1),test_export_to_file(2)
    TestListSections: test_returns_list(1),test_section_has_name(1)
    TestGetSection: test_found_section(1),test_missing_section(1)
    TestInfoSumd: test_returns_info(1)
    TestGenerateSumd: test_generate_content(0),test_generate_to_file(1)
    TestUnknownTool: test_unknown_returns_error(0)
    sumd_file(tmp_path)
    run(coro)
  tests/test_parser.py:
    e: test_parse_basic,test_parse_sections,test_validate_valid_document,test_validate_missing_intent,test_parse_file,test_parser_class,test_markpact_semantic_kinds_valid,test_markpact_unknown_kind_error,test_markpact_missing_path_error
    test_parse_basic()
    test_parse_sections()
    test_validate_valid_document()
    test_validate_missing_intent()
    test_parse_file(tmp_path)
    test_parser_class()
    test_markpact_semantic_kinds_valid()
    test_markpact_unknown_kind_error()
    test_markpact_missing_path_error()
  tests/test_pipeline.py:
    e: proj_dir,test_pipeline_run_returns_string,test_pipeline_output_has_h1,test_pipeline_output_has_metadata,test_pipeline_return_sources,test_pipeline_profile_minimal,test_pipeline_profile_refactor,test_pipeline_with_modules,test_pipeline_with_taskfile,test_pipeline_with_dependencies,test_pipeline_injects_toc,test_required_tools_rich,test_required_tools_refactor,test_required_tools_minimal,test_refresh_map_toon_writes_file,test_refresh_analysis_files_noop_without_tools
    proj_dir(tmp_path)
    test_pipeline_run_returns_string(proj_dir)
    test_pipeline_output_has_h1(proj_dir)
    test_pipeline_output_has_metadata(proj_dir)
    test_pipeline_return_sources(proj_dir)
    test_pipeline_profile_minimal(proj_dir)
    test_pipeline_profile_refactor(proj_dir)
    test_pipeline_with_modules(proj_dir)
    test_pipeline_with_taskfile(proj_dir)
    test_pipeline_with_dependencies(proj_dir)
    test_pipeline_injects_toc(proj_dir)
    test_required_tools_rich()
    test_required_tools_refactor()
    test_required_tools_minimal()
    test_refresh_map_toon_writes_file(tmp_path)
    test_refresh_analysis_files_noop_without_tools(tmp_path)
  tests/test_sections.py:
    e: make_ctx,TestMetadataSection,TestArchitectureSection,TestDependenciesSection,TestWorkflowsSection,TestQualitySection,TestEnvironmentSection,TestCallGraphSection,TestCodeAnalysisSection,TestRefactorAnalysisSection,TestSourceSnippetsSection
    TestMetadataSection: test_always_renders(0),test_contains_name_and_version(0),test_contains_metadata_header(0),test_optional_fields_omitted_when_empty(0)
    TestArchitectureSection: test_always_renders(0),test_header_present(0),test_modules_listed(0),test_no_modules_no_source_modules_section(0)
    TestDependenciesSection: test_renders_when_deps_present(0),test_runtime_deps_listed(0),test_no_deps_shows_fallback(0),test_dev_deps_section(0)
    TestWorkflowsSection: test_no_render_when_empty(0),test_renders_with_tasks(0),test_header_present(0)
    TestQualitySection: test_no_render_when_empty(0),test_renders_with_pyqual(0),test_pipeline_name_in_output(0)
    TestEnvironmentSection: test_no_render_when_empty(0),test_renders_with_vars(0)
    TestCallGraphSection: test_no_render_without_calls(0),test_no_render_without_calls_file(0),test_renders_with_calls_file(0)
    TestCodeAnalysisSection: test_no_render_when_only_calls(0),test_renders_with_map(0)
    TestRefactorAnalysisSection: test_no_render_when_empty(0),test_renders_with_analysis_files(0),test_map_toon_excluded(0)
    TestSourceSnippetsSection: test_no_render_when_empty(0),test_renders_with_snippets(0)
    make_ctx()
  tests/test_statement.py:
    e: test_placeholder,test_import
    test_placeholder()
    test_import()
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `sumd.cli` (`sumd/cli.py`)

```python
def _detect_project_type(proj_dir)  # CC=8, fan=4
def _render_doql_boilerplate(project_name, spec, extra_workflows)  # CC=4, fan=3
def _node_framework(deps)  # CC=5, fan=0
def _node_spec_from_package_json(pkg_json)  # CC=7, fan=5
def _build_doql_spec(proj_dir, project_type)  # CC=3, fan=4
def _generate_doql_less(proj_dir, project_name, version, force, project_type)  # CC=7, fan=8
def cli()  # CC=1, fan=2
def validate(file)  # CC=4, fan=8
def export(file, format, output)  # CC=8, fan=11
def info(file)  # CC=3, fan=7
def generate(file, format, output)  # CC=8, fan=15
def extract(file, section)  # CC=5, fan=8
def _is_project_dir(d)  # CC=8, fan=4
def _walk_projects(path, projects, max_depth, depth)  # CC=10, fan=7 ⚠
def _detect_projects(workspace, max_depth)  # CC=1, fan=1
def _ensure_venv(tools_dir, venv_dir, tool_list)  # CC=4, fan=4
def _tool_bin(bin_dir, name)  # CC=2, fan=1
def _run_one_tool(tool, bin_dir, proj_dir, project_output)  # CC=3, fan=5
def _run_analysis_tools(proj_dir, tool_list, skip_tools)  # CC=5, fan=5
def _export_sumd_json(proj_dir, doc)  # CC=2, fan=2
def _render_write_validate(proj_dir, sumd_path, raw, profile)  # CC=5, fan=5
def _echo_scan_result(proj_dir, doc, sources, cb_warnings)  # CC=2, fan=3
def _maybe_generate_doql(proj_dir, fix)  # CC=7, fan=6
def _finalize_scan(proj_dir, doc, sources, cb_warnings, export_json, run_analyze, tool_list, doql_sync, sumd_path)  # CC=9, fan=9
def _scan_one_project(proj_dir, fix, raw, export_json, run_analyze, tool_list, parser_inst, profile, generate_doql, doql_sync)  # CC=9, fan=8
def scan(workspace, export_json, report, fix, raw, analyze, tools, profile, depth, generate_doql, doql_sync)  # CC=10, fan=18 ⚠
def lint(files, workspace, as_json)  # CC=10, fan=12 ⚠
def _lint_collect_paths(files, workspace)  # CC=6, fan=7
def _lint_print_result(path, r)  # CC=9, fan=2
def _setup_tools_venv(venv_dir, tool_list, force)  # CC=7, fan=6
def _run_code2llm_formats(bin_dir, project, project_output)  # CC=5, fan=4
def _run_tool_subprocess(bin_dir, tool, cmd_args)  # CC=3, fan=4
def analyze(project, tools, force)  # CC=11, fan=17 ⚠
def _api_scenario_template(name, scenario_type, endpoints_block, base_path)  # CC=1, fan=3
def _scaffold_write(path, content, force, generated, skipped)  # CC=3, fan=3
def _scaffold_smoke_scenario(paths, base, out_dir, force, generated, skipped)  # CC=6, fan=5
def _scaffold_crud_scenarios(groups, base, out_dir, force, generated, skipped)  # CC=5, fan=7
def _scaffold_from_openapi(spec, out_dir, scenario_type, force, generated, skipped)  # CC=7, fan=12
def _scaffold_generic(out_dir, force, generated, skipped)  # CC=1, fan=3
def scaffold(project, output, force, scenario_type)  # CC=9, fan=18
def map_cmd(project, output, force, stdout)  # CC=7, fan=12
def main()  # CC=10, fan=3 ⚠
def main_sumr()  # CC=3, fan=2
```

### `sumd.extractor` (`sumd/extractor.py`)

```python
def _read_toml(path)  # CC=2, fan=2
def extract_pyproject(proj_dir)  # CC=3, fan=5
def _first_task_cmd(cmds)  # CC=4, fan=2
def extract_taskfile(proj_dir)  # CC=6, fan=8
def _parse_openapi_endpoints(paths)  # CC=8, fan=7
def extract_openapi(proj_dir)  # CC=5, fan=7
def _parse_doql_entities(content)  # CC=4, fan=5
def _parse_doql_interfaces(content)  # CC=3, fan=7
def _parse_doql_workflows(content)  # CC=7, fan=10
def _parse_doql_content(content)  # CC=6, fan=14
def extract_doql(proj_dir)  # CC=3, fan=3
def extract_pyqual(proj_dir)  # CC=5, fan=5
def extract_python_modules(proj_dir, pkg_name)  # CC=4, fan=4
def extract_readme_title(proj_dir)  # CC=4, fan=5
def extract_requirements(proj_dir)  # CC=7, fan=7
def extract_makefile(proj_dir)  # CC=7, fan=9
def extract_goal(proj_dir)  # CC=3, fan=7
def extract_env(proj_dir)  # CC=10, fan=9 ⚠
def _parse_dockerfile_line(line, parsed)  # CC=8, fan=6
def extract_dockerfile(proj_dir)  # CC=6, fan=5
def extract_docker_compose(proj_dir)  # CC=10, fan=12 ⚠
def extract_package_json(proj_dir)  # CC=3, fan=6
def _lang_of(path)  # CC=1, fan=2
def _fan_out(func_node)  # CC=5, fan=5
def _cc_estimate(func_node)  # CC=4, fan=4
def _try_radon_cc(src)  # CC=3, fan=1
def _analyse_py_top_funcs(tree, radon_cc)  # CC=5, fan=6
def _analyse_class_methods(node, radon_cc)  # CC=6, fan=6
def _analyse_py_top_classes(tree, radon_cc)  # CC=5, fan=7
def _analyse_py_module(path)  # CC=2, fan=6
def _is_map_ignored_path(p)  # CC=4, fan=1
def _collect_map_files(proj_dir)  # CC=7, fan=10
def _render_map_detail(proj_dir, modules)  # CC=5, fan=3
def _map_cc_stats(all_funcs)  # CC=12, fan=8 ⚠
def _render_py_module_detail(rel, info, a)  # CC=7, fan=3
def generate_map_toon(proj_dir)  # CC=5, fan=13
def required_tools_for_profile(profile)  # CC=4, fan=0
def extract_source_snippets(proj_dir, pkg_name)  # CC=6, fan=11
def extract_project_analysis(proj_dir, refactor)  # CC=6, fan=7
```

### `sumd.pipeline` (`sumd/pipeline.py`)

```python
def _refresh_map_toon(proj_dir)  # CC=3, fan=3
def _find_tools_bin_dir(proj_dir)  # CC=3, fan=1
def _run_tool_if_present(bin_dir, name, args, proj_dir)  # CC=3, fan=3
def _refresh_analysis_files(proj_dir, profile)  # CC=7, fan=5
def _collect_tool_sources(pyproj, reqs, tasks, makefile, scenarios)  # CC=7, fan=3
def _doql_sources(doql)  # CC=4, fan=1
def _collect_pkg_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars)  # CC=5, fan=6
def _collect_infra_sources(dockerfile, compose, pkg_json, modules, project_analysis)  # CC=6, fan=3
def _collect_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars, dockerfile, compose, pkg_json, modules, project_analysis)  # CC=1, fan=2
def _inject_toc(content)  # CC=3, fan=6
class RenderPipeline:  # Collect project data → build sections → render → inject TOC.
    def __init__(proj_dir, raw_sources)  # CC=1
    def _collect()  # CC=3
    def _build_registered_sections(ctx, profile)  # CC=4
    def _render_legacy_sections(ctx)  # CC=1
    def _assemble(ctx, profile)  # CC=4
    def run(profile, return_sources)  # CC=2
```

### `sumd.validator` (`sumd/validator.py`)

```python
def _validate_yaml_body(body, path)  # CC=2, fan=1
def _validate_less_css_body(body, path)  # CC=2, fan=1
def _validate_mermaid_body(body, path)  # CC=3, fan=4
def _validate_toon_body(body, path)  # CC=2, fan=1
def _validate_bash_body(body, path)  # CC=4, fan=1
def _validate_deps_body(body, path)  # CC=5, fan=6
def _validate_markpact_meta(mp, line_no, lang, meta, issues)  # CC=5, fan=6
def validate_codeblocks(content, source)  # CC=9, fan=11
def _check_h1(lines, source)  # CC=3, fan=2
def _check_required_sections(lines, source, profile)  # CC=7, fan=6
def _check_metadata_fields(lines, source)  # CC=9, fan=6
def _check_unclosed_fences(lines, source)  # CC=4, fan=2
def _check_empty_links(content, source)  # CC=2, fan=1
def validate_markdown(content, source, profile)  # CC=1, fan=6
def validate_sumd_file(path, profile)  # CC=3, fan=5
class CodeBlockIssue:
```

### `sumd.mcp_server` (`sumd/mcp_server.py`)

```python
def _doc_to_dict(doc)  # CC=2, fan=0
def _resolve_path(path)  # CC=2, fan=3
def list_tools()  # CC=1, fan=2
def _tool_parse_sumd(arguments)  # CC=1, fan=5
def _tool_validate_sumd(arguments)  # CC=1, fan=7
def _tool_export_sumd(arguments)  # CC=5, fan=8
def _tool_list_sections(arguments)  # CC=2, fan=4
def _tool_get_section(arguments)  # CC=5, fan=6
def _tool_info_sumd(arguments)  # CC=2, fan=5
def _tool_generate_sumd(arguments)  # CC=5, fan=5
def call_tool(name, arguments)  # CC=3, fan=4
def main()  # CC=1, fan=3
```

## Call Graph

*171 nodes · 159 edges · 24 modules · CC̄=1.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `run` *(in examples.mcp.mcp_client)* | 11 ⚠ | 1 | 53 | **54** |
| `print` *(in README)* | 0 | 42 | 0 | **42** |
| `analyze` *(in sumd.cli)* | 11 ⚠ | 0 | 33 | **33** |
| `_collect` *(in sumd.pipeline.RenderPipeline)* | 3 | 0 | 30 | **30** |
| `_render_call_graph` *(in sumd.sections.call_graph)* | 7 | 1 | 28 | **29** |
| `_render_api_stubs` *(in sumd.sections.api_stubs)* | 11 ⚠ | 1 | 27 | **28** |
| `generate_map_toon` *(in sumd.extractor)* | 5 | 2 | 24 | **26** |
| `_render_quality_parsed` *(in sumd.sections.quality)* | 9 | 1 | 21 | **22** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 171 | edges: 159 | modules: 24
# CC̄=1.2

HUBS[20]:
  examples.mcp.mcp_client.run
    CC=11  in:1  out:53  total:54
  README.print
    CC=0  in:42  out:0  total:42
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:30  total:30
  sumd.sections.call_graph._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.sections.api_stubs._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.extractor.generate_map_toon
    CC=5  in:2  out:24  total:26
  sumd.sections.quality._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.sections.dependencies._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.sections.interfaces._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor.extract_pyproject
    CC=3  in:2  out:17  total:19
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.validator.validate_codeblocks
    CC=9  in:1  out:17  total:18
  sumd.sections.environment._render_goal_section
    CC=9  in:1  out:17  total:18
  sumd.extractor.extract_package_json
    CC=3  in:3  out:15  total:18
  sumd.sections.workflows._render_workflows_taskfile
    CC=6  in:1  out:17  total:18
  sumd.sections.source_snippets._render_source_snippets
    CC=8  in:1  out:16  total:17

MODULES:
  README  [1 funcs]
    print  CC=0  out:0
  examples.llm.anthropic_example  [2 funcs]
    ask  CC=1  out:3
    main  CC=2  out:14
  examples.llm.openai_example  [3 funcs]
    ask  CC=1  out:3
    build_context  CC=5  out:9
    main  CC=2  out:15
  examples.mcp.mcp_client  [2 funcs]
    main  CC=3  out:12
    run  CC=11  out:53
  sumd.cli  [37 funcs]
    _api_scenario_template  CC=1  out:3
    _build_doql_spec  CC=3  out:4
    _detect_project_type  CC=8  out:4
    _detect_projects  CC=1  out:1
    _echo_scan_result  CC=2  out:4
    _ensure_venv  CC=4  out:7
    _export_sumd_json  CC=2  out:2
    _finalize_scan  CC=9  out:16
    _generate_doql_less  CC=7  out:10
    _is_project_dir  CC=8  out:4
  sumd.extractor  [33 funcs]
    _analyse_class_methods  CC=6  out:6
    _analyse_py_module  CC=2  out:6
    _analyse_py_top_classes  CC=5  out:8
    _analyse_py_top_funcs  CC=5  out:7
    _cc_estimate  CC=4  out:4
    _collect_map_files  CC=7  out:11
    _fan_out  CC=5  out:8
    _first_task_cmd  CC=4  out:4
    _is_map_ignored_path  CC=4  out:1
    _lang_of  CC=1  out:2
  sumd.mcp_server  [9 funcs]
    _doc_to_dict  CC=2  out:0
    _resolve_path  CC=2  out:4
    _tool_export_sumd  CC=5  out:12
    _tool_generate_sumd  CC=5  out:11
    _tool_get_section  CC=5  out:8
    _tool_info_sumd  CC=2  out:5
    _tool_list_sections  CC=2  out:4
    _tool_parse_sumd  CC=1  out:5
    _tool_validate_sumd  CC=1  out:7
  sumd.parser  [1 funcs]
    parse_file  CC=1  out:2
  sumd.pipeline  [12 funcs]
    _collect  CC=3  out:30
    run  CC=2  out:3
    _collect_infra_sources  CC=6  out:10
    _collect_pkg_sources  CC=5  out:11
    _collect_sources  CC=1  out:2
    _collect_tool_sources  CC=7  out:6
    _doql_sources  CC=4  out:4
    _find_tools_bin_dir  CC=3  out:1
    _inject_toc  CC=3  out:9
    _refresh_analysis_files  CC=7  out:11
  sumd.sections.api_stubs  [2 funcs]
    render  CC=1  out:1
    _render_api_stubs  CC=11  out:27
  sumd.sections.architecture  [8 funcs]
    render  CC=1  out:1
    _render_architecture  CC=6  out:12
    _render_architecture_doql_parsed  CC=1  out:4
    _render_architecture_doql_section  CC=6  out:14
    _render_doql_app  CC=3  out:8
    _render_doql_entities  CC=6  out:9
    _render_doql_integrations  CC=5  out:9
    _render_doql_interfaces  CC=6  out:10
  sumd.sections.call_graph  [7 funcs]
    render  CC=1  out:1
    _parse_calls_header  CC=6  out:12
    _parse_calls_hubs  CC=8  out:4
    _parse_calls_toon  CC=1  out:3
    _parse_hub_stat_line  CC=2  out:9
    _process_in_hubs_line  CC=6  out:6
    _render_call_graph  CC=7  out:28
  sumd.sections.code_analysis  [2 funcs]
    render  CC=1  out:1
    _render_code_analysis  CC=9  out:15
  sumd.sections.configuration  [2 funcs]
    render  CC=1  out:1
    _render_configuration_section  CC=1  out:0
  sumd.sections.dependencies  [4 funcs]
    render  CC=1  out:1
    _render_dependencies  CC=2  out:6
    _render_deps_dev  CC=6  out:15
    _render_deps_runtime  CC=6  out:19
  sumd.sections.deployment  [6 funcs]
    render  CC=1  out:1
    _render_deployment  CC=1  out:5
    _render_deployment_docker  CC=8  out:7
    _render_deployment_install  CC=2  out:11
    _render_deployment_reqs  CC=5  out:9
    _render_dockerfile_info  CC=6  out:9
  sumd.sections.environment  [3 funcs]
    render  CC=1  out:4
    _render_env_section  CC=3  out:7
    _render_goal_section  CC=9  out:17
  sumd.sections.extras  [4 funcs]
    render  CC=1  out:1
    _render_extras  CC=3  out:3
    _render_makefile_targets  CC=3  out:4
    _render_pkg_json_scripts  CC=7  out:16
  sumd.sections.interfaces  [7 funcs]
    render  CC=1  out:1
    _render_interfaces  CC=5  out:9
    _render_interfaces_openapi  CC=6  out:19
    _render_interfaces_testql  CC=3  out:4
    _render_testql_extras  CC=7  out:9
    _render_testql_one_structured  CC=7  out:13
    _render_testql_raw  CC=4  out:12
  sumd.sections.quality  [4 funcs]
    render  CC=1  out:1
    _render_quality  CC=3  out:4
    _render_quality_parsed  CC=9  out:21
    _render_quality_raw  CC=2  out:7
  sumd.sections.source_snippets  [2 funcs]
    render  CC=1  out:1
    _render_source_snippets  CC=8  out:16
  sumd.sections.workflows  [4 funcs]
    render  CC=1  out:1
    _render_workflows  CC=4  out:5
    _render_workflows_doql  CC=4  out:7
    _render_workflows_taskfile  CC=6  out:17
  sumd.toon_parser  [7 funcs]
    _parse_toon_block_api  CC=6  out:4
    _parse_toon_block_assert  CC=7  out:9
    _parse_toon_block_config  CC=9  out:8
    _parse_toon_block_navigate  CC=7  out:5
    _parse_toon_block_performance  CC=7  out:8
    _parse_toon_file  CC=4  out:16
    extract_testql_scenarios  CC=7  out:12
  sumd.validator  [9 funcs]
    _check_empty_links  CC=2  out:1
    _check_h1  CC=3  out:2
    _check_metadata_fields  CC=9  out:7
    _check_required_sections  CC=7  out:6
    _check_unclosed_fences  CC=4  out:2
    _validate_markpact_meta  CC=5  out:9
    validate_codeblocks  CC=9  out:17
    validate_markdown  CC=1  out:6
    validate_sumd_file  CC=3  out:5

EDGES:
  examples.llm.anthropic_example.ask → sumd.parser.SUMDParser.parse_file
  examples.llm.anthropic_example.main → README.print
  examples.llm.anthropic_example.main → examples.llm.anthropic_example.ask
  examples.llm.openai_example.build_context → sumd.parser.SUMDParser.parse_file
  examples.llm.openai_example.ask → examples.llm.openai_example.build_context
  examples.llm.openai_example.main → README.print
  examples.mcp.mcp_client.run → README.print
  examples.mcp.mcp_client.main → README.print
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_config
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_api
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_assert
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_performance
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_navigate
  sumd.toon_parser.extract_testql_scenarios → sumd.toon_parser._parse_toon_file
  sumd.validator.validate_codeblocks → sumd.validator._validate_markpact_meta
  sumd.validator.validate_markdown → sumd.validator._check_empty_links
  sumd.validator.validate_markdown → sumd.validator._check_unclosed_fences
  sumd.validator.validate_markdown → sumd.validator._check_metadata_fields
  sumd.validator.validate_markdown → sumd.validator._check_h1
  sumd.validator.validate_markdown → sumd.validator._check_required_sections
  sumd.validator.validate_sumd_file → sumd.validator.validate_markdown
  sumd.validator.validate_sumd_file → sumd.validator.validate_codeblocks
  sumd.cli._node_spec_from_package_json → sumd.cli._node_framework
  sumd.cli._build_doql_spec → sumd.extractor.extract_package_json
  sumd.cli._build_doql_spec → sumd.cli._node_spec_from_package_json
  sumd.cli._generate_doql_less → sumd.cli._build_doql_spec
  sumd.cli._generate_doql_less → sumd.cli._render_doql_boilerplate
  sumd.cli.validate → sumd.parser.SUMDParser.parse_file
  sumd.cli.export → sumd.parser.SUMDParser.parse_file
  sumd.cli.info → sumd.parser.SUMDParser.parse_file
  sumd.cli.extract → sumd.parser.SUMDParser.parse_file
  sumd.cli._walk_projects → sumd.cli._is_project_dir
  sumd.cli._detect_projects → sumd.cli._walk_projects
  sumd.cli._run_one_tool → sumd.cli._tool_bin
  sumd.cli._run_analysis_tools → sumd.cli._ensure_venv
  sumd.cli._run_analysis_tools → sumd.cli._run_one_tool
  sumd.cli._render_write_validate → sumd.validator.validate_sumd_file
  sumd.cli._render_write_validate → sumd.parser.SUMDParser.parse_file
  sumd.cli._maybe_generate_doql → sumd.cli._detect_project_type
  sumd.cli._maybe_generate_doql → sumd.extractor.extract_pyproject
  sumd.cli._maybe_generate_doql → sumd.cli._generate_doql_less
  sumd.cli._maybe_generate_doql → sumd.extractor.extract_package_json
  sumd.cli._finalize_scan → sumd.cli._echo_scan_result
  sumd.cli._finalize_scan → sumd.cli._export_sumd_json
  sumd.cli._finalize_scan → sumd.cli._run_analysis_tools
  sumd.cli._scan_one_project → sumd.cli._render_write_validate
  sumd.cli._scan_one_project → sumd.cli._finalize_scan
  sumd.cli._scan_one_project → sumd.cli._maybe_generate_doql
  sumd.cli.lint → sumd.cli._lint_collect_paths
  sumd.cli.lint → sumd.validator.validate_sumd_file
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

### Smoke (1)

**`smoke-generic.testql.toon.yaml — smoke tests for sumd CLI`**
- `GET /health` → `200`
- assert `status < 500`

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation
