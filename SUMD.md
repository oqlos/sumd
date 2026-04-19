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
- **version**: `0.2.0-rc1`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(1), app.doql.css, pyqual.yaml, goal.yaml, .env.example, src(8 mod), project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.css`)

```css markpact:doql path=app.doql.css
app {
  name: "sumd";
  version: "0.1.15";
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="sumd"] {

}

workflow[name="install"] {
  trigger: "manual";
  step-1: run cmd=pip install -e .[dev];
}

workflow[name="quality"] {
  trigger: "manual";
  step-1: run cmd=pyqual run;
}

workflow[name="quality:fix"] {
  trigger: "manual";
  step-1: run cmd=pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: "manual";
  step-1: run cmd=pyqual report;
}

workflow[name="test"] {
  trigger: "manual";
  step-1: run cmd=pytest -q;
}

workflow[name="lint"] {
  trigger: "manual";
  step-1: run cmd=ruff check .;
}

workflow[name="fmt"] {
  trigger: "manual";
  step-1: run cmd=ruff format .;
}

workflow[name="build"] {
  trigger: "manual";
  step-1: run cmd=python -m build;
}

workflow[name="clean"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: "manual";
  step-1: run cmd=echo "📁 Analyzing sumd project structure..."
{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
{{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: "manual";
  step-1: run cmd={{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force;
  step-2: run cmd=echo "✅ Captured in app.doql.css";
}

workflow[name="doql:export"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "app.doql.css" ]; then
  echo "❌ app.doql.css not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} validate;
}

workflow[name="doql:doctor"] {
  trigger: "manual";
  step-1: run cmd={{.DOQL_CMD}} doctor;
}

workflow[name="doql:build"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd=# Regenerate LESS from CSS if CSS exists
if [ -f "app.doql.css" ]; then
  {{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}
fi;
  step-3: run cmd={{.DOQL_CMD}} build app.doql.css --out build/;
}

workflow[name="docs:build"] {
  trigger: "manual";
  step-1: run cmd=echo "Building SUMD documentation...";
  step-2: run cmd=python -m sumd.cli docs/ docs/;
}

workflow[name="help"] {
  trigger: "manual";
  step-1: run cmd=task --list;
}

deploy {
  target: docker-compose;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: ".env";
}
```

### Source Modules

- `sumd.cli`
- `sumd.extractor`
- `sumd.generator`
- `sumd.mcp_server`
- `sumd.parser`
- `sumd.pipeline`
- `sumd.renderer`
- `sumd.toon_parser`

## Interfaces

### CLI Entry Points

- `sumd`
- `sumr`
- `sumd-mcp`

### testql Scenarios

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
  version: 0.2.0-rc1
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
click>=8.0
pyyaml>=6.0
toml>=0.10.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov>=4.0
ruff>=0.1
build
twine
pyqual>=0.1
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
# sumd | 29f 5023L | shell:2,python:27 | 2026-04-19
# stats: 188 func | 0 cls | 29 mod | CC̄=4.5 | critical:1 | cycles:0
# alerts[5]: fan-out RenderPipeline._collect=20; fan-out scaffold=19; fan-out analyze=17; fan-out generate=17; fan-out scan=17
# hotspots[5]: RenderPipeline._collect fan=20; scaffold fan=19; generate fan=17; scan fan=17; analyze fan=17
# evolution: CC̄ 4.7→4.5 (improved -0.2)
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[29]:
  project.sh,35
  scripts/bootstrap.sh,69
  scripts/generate_all_sumd.py,22
  sumd/__init__.py,33
  sumd/cli.py,1081
  sumd/extractor.py,861
  sumd/generator.py,15
  sumd/mcp_server.py,358
  sumd/parser.py,543
  sumd/pipeline.py,226
  sumd/renderer.py,989
  sumd/sections/__init__.py,100
  sumd/sections/api_stubs.py,25
  sumd/sections/architecture.py,23
  sumd/sections/base.py,93
  sumd/sections/call_graph.py,27
  sumd/sections/code_analysis.py,25
  sumd/sections/configuration.py,21
  sumd/sections/dependencies.py,26
  sumd/sections/deployment.py,23
  sumd/sections/environment.py,24
  sumd/sections/extras.py,21
  sumd/sections/interfaces.py,23
  sumd/sections/metadata.py,51
  sumd/sections/quality.py,21
  sumd/sections/refactor_analysis.py,68
  sumd/sections/source_snippets.py,26
  sumd/sections/workflows.py,21
  sumd/toon_parser.py,173
D:
  sumd/renderer.py:
    e: _render_architecture_doql_section,_render_architecture_modules,_render_architecture,_render_doql_app,_render_doql_entities,_render_doql_interfaces,_render_doql_integrations,_render_architecture_doql_parsed,_render_interfaces,_render_interfaces_openapi,_render_testql_raw,_render_testql_endpoint,_render_testql_extras,_render_testql_one_structured,_render_interfaces_testql,_render_workflows_doql,_render_workflows_taskfile,_render_workflows,_render_quality_raw,_render_quality_parsed,_render_quality,_render_deps_runtime,_render_deps_dev,_render_dependencies,_render_deployment_install,_render_deployment_reqs,_render_deployment_docker,_render_deployment,_render_extras,_render_code_analysis,_render_source_snippets,_render_api_stubs,_render_test_contracts,_parse_calls_header,_parse_calls_hubs,_parse_calls_toon,_render_call_graph,_collect_pkg_sources,_collect_infra_sources,_collect_sources,_render_metadata_section,_render_configuration_section,_render_env_section,_render_goal_section,_inject_toc,generate_sumd_content
    _render_architecture_doql_section(doql;proj_dir;raw_sources;L)
    _render_architecture_modules(modules;name;L)
    _render_architecture(doql;modules;name;proj_dir;raw_sources)
    _render_doql_app(doql;L)
    _render_doql_entities(doql;L)
    _render_doql_interfaces(doql;L)
    _render_doql_integrations(doql;L)
    _render_architecture_doql_parsed(doql;L)
    _render_interfaces(scripts;openapi;scenarios;proj_dir;raw_sources)
    _render_interfaces_openapi(openapi;proj_dir;raw_sources;L)
    _render_testql_raw(scenarios;proj_dir;L)
    _render_testql_endpoint(ep;L)
    _render_testql_extras(sc;L)
    _render_testql_one_structured(sc;L)
    _render_interfaces_testql(scenarios;proj_dir;raw_sources;L)
    _render_workflows_doql(doql;L)
    _render_workflows_taskfile(tasks;proj_dir;raw_sources;L)
    _render_workflows(doql;tasks;proj_dir;raw_sources)
    _render_quality_raw(proj_dir;L)
    _render_quality_parsed(pyqual;L)
    _render_quality(pyqual;proj_dir;raw_sources)
    _render_deps_runtime(deps;node_deps;L)
    _render_deps_dev(dev_deps;node_dev;L)
    _render_dependencies(deps;dev_deps;pkg_json)
    _render_deployment_install(pkg_json;name;L)
    _render_deployment_reqs(reqs;L)
    _render_deployment_docker(dockerfile;compose;L)
    _render_deployment(pkg_json;name;reqs;dockerfile;compose)
    _render_extras(makefile;pkg_json)
    _render_code_analysis(project_analysis;skip_files)
    _render_source_snippets(source_snippets;top_n)
    _render_api_stubs(openapi)
    _render_test_contracts(scenarios)
    _parse_calls_header(lines)
    _parse_calls_hubs(lines)
    _parse_calls_toon(content)
    _render_call_graph(project_analysis)
    _collect_pkg_sources(pyproj;reqs;tasks;makefile;scenarios;openapi;doql;pyqual;goal;env_vars)
    _collect_infra_sources(dockerfile;compose;pkg_json;modules;project_analysis)
    _collect_sources(pyproj;reqs;tasks;makefile;scenarios;openapi;doql;pyqual;goal;env_vars;dockerfile;compose;pkg_json;modules;project_analysis)
    _render_metadata_section(name;version;py_req;license_;ai_model;openapi;sources_used)
    _render_configuration_section(name;version)
    _render_env_section(env_vars)
    _render_goal_section(goal)
    _inject_toc(content)
    generate_sumd_content(proj_dir;return_sources;raw_sources;profile)
  sumd/extractor.py:
    e: _read_toml,extract_pyproject,extract_taskfile,extract_openapi,_parse_doql_entities,_parse_doql_interfaces,_parse_doql_workflows,_parse_doql_content,extract_doql,extract_pyqual,extract_python_modules,extract_readme_title,extract_requirements,extract_makefile,extract_goal,extract_env,extract_dockerfile,extract_docker_compose,extract_package_json,_lang_of,_fan_out,_cc_estimate,_try_radon_cc,_analyse_py_top_funcs,_analyse_py_top_classes,_analyse_py_module,_collect_map_files,_render_map_detail,_map_cc_stats,generate_map_toon,extract_source_snippets,extract_project_analysis
    _read_toml(path)
    extract_pyproject(proj_dir)
    extract_taskfile(proj_dir)
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
    extract_dockerfile(proj_dir)
    extract_docker_compose(proj_dir)
    extract_package_json(proj_dir)
    _lang_of(path)
    _fan_out(func_node)
    _cc_estimate(func_node)
    _try_radon_cc(src)
    _analyse_py_top_funcs(tree;radon_cc)
    _analyse_py_top_classes(tree;radon_cc)
    _analyse_py_module(path)
    _collect_map_files(proj_dir)
    _render_map_detail(proj_dir;modules)
    _map_cc_stats(all_funcs)
    generate_map_toon(proj_dir)
    extract_source_snippets(proj_dir;pkg_name)
    extract_project_analysis(proj_dir;refactor)
  sumd/parser.py:
    e: SectionType,Section,SUMDDocument,SUMDParser,CodeBlockIssue,parse,parse_file,validate,_validate_yaml_body,_validate_less_css_body,_validate_mermaid_body,_validate_toon_body,_validate_bash_body,_validate_deps_body,validate_codeblocks,_check_h1,_check_required_sections,_check_metadata_fields,_check_unclosed_fences,_check_empty_links,validate_markdown,validate_sumd_file
    SectionType(Enum):  # SUMD section types...
    Section:  # Represents a SUMD section...
    SUMDDocument:  # Represents a parsed SUMD document...
    SUMDParser: __init__(0),parse(1),parse_file(1),_parse_header(1),_parse_sections(1),validate(1)  # Parser for SUMD markdown documents...
    CodeBlockIssue:
    parse(content)
    parse_file(path)
    validate(document)
    _validate_yaml_body(body;path)
    _validate_less_css_body(body;path)
    _validate_mermaid_body(body;path)
    _validate_toon_body(body;path)
    _validate_bash_body(body;path)
    _validate_deps_body(body;path)
    validate_codeblocks(content;source)
    _check_h1(lines;source)
    _check_required_sections(lines;source;profile)
    _check_metadata_fields(lines;source)
    _check_unclosed_fences(lines;source)
    _check_empty_links(content;source)
    validate_markdown(content;source;profile)
    validate_sumd_file(path;profile)
  sumd/cli.py:
    e: cli,validate,export,info,generate,extract,_detect_projects,_run_analysis_tools,_export_sumd_json,_render_write_validate,_scan_one_project,scan,lint,_lint_collect_paths,_lint_print_result,_setup_tools_venv,_run_code2llm_formats,_run_tool_subprocess,analyze,_api_scenario_template,_scaffold_write,_scaffold_smoke_scenario,_scaffold_crud_scenarios,_scaffold_from_openapi,_scaffold_generic,scaffold,map_cmd,main,main_sumr
    cli()
    validate(file)
    export(file;format;output)
    info(file)
    generate(file;format;output)
    extract(file;section)
    _detect_projects(workspace;max_depth)
    _run_analysis_tools(proj_dir;tool_list)
    _export_sumd_json(proj_dir;doc)
    _render_write_validate(proj_dir;sumd_path;raw;profile)
    _scan_one_project(proj_dir;fix;raw;export_json;run_analyze;tool_list;parser_inst;profile)
    scan(workspace;export_json;report;fix;raw;analyze;tools;profile;depth)
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
  sumd/sections/metadata.py:
    e: MetadataSection
    MetadataSection: should_render(1),render(1)  # Render ## Metadata — always present, all profiles...
  sumd/pipeline.py:
    e: RenderPipeline
    RenderPipeline: __init__(2),_collect(0),_build_registered_sections(2),_render_legacy_sections(1),_assemble(2),run(2)  # Collect project data → build sections → render → inject TOC...
  sumd/sections/dependencies.py:
    e: DependenciesSection
    DependenciesSection: should_render(1),render(1)
  sumd/sections/interfaces.py:
    e: InterfacesSection
    InterfacesSection: should_render(1),render(1)
  sumd/sections/refactor_analysis.py:
    e: RefactorAnalysisSection
    RefactorAnalysisSection: should_render(1),render(1)
  sumd/sections/code_analysis.py:
    e: CodeAnalysisSection
    CodeAnalysisSection: should_render(1),render(1)
  sumd/sections/call_graph.py:
    e: CallGraphSection
    CallGraphSection: should_render(1),render(1)
  sumd/sections/workflows.py:
    e: WorkflowsSection
    WorkflowsSection: should_render(1),render(1)
  sumd/sections/extras.py:
    e: ExtrasSection
    ExtrasSection: should_render(1),render(1)
  sumd/sections/environment.py:
    e: EnvironmentSection
    EnvironmentSection: should_render(1),render(1)
  sumd/sections/quality.py:
    e: QualitySection
    QualitySection: should_render(1),render(1)
  sumd/sections/deployment.py:
    e: DeploymentSection
    DeploymentSection: should_render(1),render(1)
  sumd/sections/architecture.py:
    e: ArchitectureSection
    ArchitectureSection: should_render(1),render(1)
  sumd/sections/source_snippets.py:
    e: SourceSnippetsSection
    SourceSnippetsSection: should_render(1),render(1)
  sumd/sections/api_stubs.py:
    e: ApiStubsSection
    ApiStubsSection: should_render(1),render(1)
  sumd/sections/configuration.py:
    e: ConfigurationSection
    ConfigurationSection: should_render(1),render(1)
  sumd/sections/base.py:
    e: RenderContext,Section
    RenderContext:  # All extracted data for a project, passed to every Section.re...
    Section(Protocol): should_render(1),render(1)  # Protocol for all SUMD section renderers.

Attributes:
    na...
  project.sh:
  sumd/generator.py:
  sumd/__init__.py:
  sumd/sections/__init__.py:
  scripts/bootstrap.sh:
  scripts/generate_all_sumd.py:
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `sumd.renderer` (`sumd/renderer.py`)

```python
def _render_architecture_doql_section(doql, proj_dir, raw_sources, L)  # CC=4, fan=8
def _render_architecture_modules(modules, name, L)  # CC=2, fan=1
def _render_architecture(doql, modules, name, proj_dir, raw_sources)  # CC=6, fan=4
def _render_doql_app(doql, L)  # CC=3, fan=3
def _render_doql_entities(doql, L)  # CC=4, fan=4
def _render_doql_interfaces(doql, L)  # CC=3, fan=5
def _render_doql_integrations(doql, L)  # CC=3, fan=5
def _render_architecture_doql_parsed(doql, L)  # CC=1, fan=4
def _render_interfaces(scripts, openapi, scenarios, proj_dir, raw_sources)  # CC=5, fan=4
def _render_interfaces_openapi(openapi, proj_dir, raw_sources, L)  # CC=5, fan=7
def _render_testql_raw(scenarios, proj_dir, L)  # CC=4, fan=7
def _render_testql_endpoint(ep, L)  # CC=1, fan=2
def _render_testql_extras(sc, L)  # CC=6, fan=3
def _render_testql_one_structured(sc, L)  # CC=7, fan=4
def _render_interfaces_testql(scenarios, proj_dir, raw_sources, L)  # CC=3, fan=3
def _render_workflows_doql(doql, L)  # CC=2, fan=3
def _render_workflows_taskfile(tasks, proj_dir, raw_sources, L)  # CC=6, fan=4
def _render_workflows(doql, tasks, proj_dir, raw_sources)  # CC=4, fan=4
def _render_quality_raw(proj_dir, L)  # CC=2, fan=4
def _render_quality_parsed(pyqual, L)  # CC=8, fan=3
def _render_quality(pyqual, proj_dir, raw_sources)  # CC=3, fan=3
def _render_deps_runtime(deps, node_deps, L)  # CC=6, fan=2
def _render_deps_dev(dev_deps, node_dev, L)  # CC=6, fan=2
def _render_dependencies(deps, dev_deps, pkg_json)  # CC=2, fan=4
def _render_deployment_install(pkg_json, name, L)  # CC=2, fan=2
def _render_deployment_reqs(reqs, L)  # CC=5, fan=2
def _render_deployment_docker(dockerfile, compose, L)  # CC=8, fan=4
def _render_deployment(pkg_json, name, reqs, dockerfile, compose)  # CC=1, fan=4
def _render_extras(makefile, pkg_json)  # CC=9, fan=4
def _render_code_analysis(project_analysis, skip_files)  # CC=6, fan=4
def _render_source_snippets(source_snippets, top_n)  # CC=6, fan=4
def _render_api_stubs(openapi)  # CC=8, fan=9
def _render_test_contracts(scenarios)  # CC=12, fan=8 ⚠
def _parse_calls_header(lines)  # CC=6, fan=5
def _parse_calls_hubs(lines)  # CC=15, fan=7 ⚠
def _parse_calls_toon(content)  # CC=1, fan=3
def _render_call_graph(project_analysis)  # CC=4, fan=8
def _collect_pkg_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars)  # CC=13, fan=4 ⚠
def _collect_infra_sources(dockerfile, compose, pkg_json, modules, project_analysis)  # CC=6, fan=3
def _collect_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars, dockerfile, compose, pkg_json, modules, project_analysis)  # CC=1, fan=2
def _render_metadata_section(name, version, py_req, license_, ai_model, openapi, sources_used)  # CC=5, fan=3
def _render_configuration_section(name, version)  # CC=1, fan=0
def _render_env_section(env_vars)  # CC=3, fan=2
def _render_goal_section(goal)  # CC=7, fan=3
def _inject_toc(content)  # CC=3, fan=6
def generate_sumd_content(proj_dir, return_sources, raw_sources, profile)  # CC=1, fan=2
```

### `sumd.extractor` (`sumd/extractor.py`)

```python
def _read_toml(path)  # CC=2, fan=2
def extract_pyproject(proj_dir)  # CC=3, fan=5
def extract_taskfile(proj_dir)  # CC=10, fan=7 ⚠
def extract_openapi(proj_dir)  # CC=12, fan=12 ⚠
def _parse_doql_entities(content)  # CC=4, fan=5
def _parse_doql_interfaces(content)  # CC=3, fan=7
def _parse_doql_workflows(content)  # CC=3, fan=10
def _parse_doql_content(content)  # CC=5, fan=14
def extract_doql(proj_dir)  # CC=3, fan=3
def extract_pyqual(proj_dir)  # CC=3, fan=5
def extract_python_modules(proj_dir, pkg_name)  # CC=2, fan=4
def extract_readme_title(proj_dir)  # CC=4, fan=5
def extract_requirements(proj_dir)  # CC=7, fan=7
def extract_makefile(proj_dir)  # CC=7, fan=9
def extract_goal(proj_dir)  # CC=3, fan=7
def extract_env(proj_dir)  # CC=8, fan=9
def extract_dockerfile(proj_dir)  # CC=12, fan=9 ⚠
def extract_docker_compose(proj_dir)  # CC=9, fan=12
def extract_package_json(proj_dir)  # CC=3, fan=6
def _lang_of(path)  # CC=1, fan=2
def _fan_out(func_node)  # CC=5, fan=5
def _cc_estimate(func_node)  # CC=4, fan=4
def _try_radon_cc(src)  # CC=2, fan=1
def _analyse_py_top_funcs(tree, radon_cc)  # CC=4, fan=6
def _analyse_py_top_classes(tree, radon_cc)  # CC=9, fan=9
def _analyse_py_module(path)  # CC=2, fan=6
def _collect_map_files(proj_dir)  # CC=10, fan=11 ⚠
def _render_map_detail(proj_dir, modules)  # CC=5, fan=3
def _map_cc_stats(all_funcs)  # CC=6, fan=8
def generate_map_toon(proj_dir)  # CC=7, fan=12
def extract_source_snippets(proj_dir, pkg_name)  # CC=6, fan=11
def extract_project_analysis(proj_dir, refactor)  # CC=5, fan=7
```

### `sumd.cli` (`sumd/cli.py`)

```python
def cli()  # CC=1, fan=2
def validate(file)  # CC=4, fan=8
def export(file, format, output)  # CC=7, fan=11
def info(file)  # CC=3, fan=7
def generate(file, format, output)  # CC=8, fan=15
def extract(file, section)  # CC=5, fan=8
def _detect_projects(workspace, max_depth)  # CC=9, fan=7
def _run_analysis_tools(proj_dir, tool_list)  # CC=8, fan=4
def _export_sumd_json(proj_dir, doc)  # CC=1, fan=2
def _render_write_validate(proj_dir, sumd_path, raw, profile)  # CC=1, fan=5
def _scan_one_project(proj_dir, fix, raw, export_json, run_analyze, tool_list, parser_inst, profile)  # CC=8, fan=8
def scan(workspace, export_json, report, fix, raw, analyze, tools, profile, depth)  # CC=8, fan=17
def lint(files, workspace, as_json)  # CC=5, fan=12
def _lint_collect_paths(files, workspace)  # CC=4, fan=7
def _lint_print_result(path, r)  # CC=3, fan=2
def _setup_tools_venv(venv_dir, tool_list, force)  # CC=6, fan=6
def _run_code2llm_formats(bin_dir, project, project_output)  # CC=4, fan=4
def _run_tool_subprocess(bin_dir, tool, cmd_args)  # CC=3, fan=4
def analyze(project, tools, force)  # CC=8, fan=17
def _api_scenario_template(name, scenario_type, endpoints_block, base_path)  # CC=1, fan=3
def _scaffold_write(path, content, force, generated, skipped)  # CC=3, fan=3
def _scaffold_smoke_scenario(paths, base, out_dir, force, generated, skipped)  # CC=1, fan=5
def _scaffold_crud_scenarios(groups, base, out_dir, force, generated, skipped)  # CC=4, fan=7
def _scaffold_from_openapi(spec, out_dir, scenario_type, force, generated, skipped)  # CC=7, fan=12
def _scaffold_generic(out_dir, force, generated, skipped)  # CC=1, fan=3
def scaffold(project, output, force, scenario_type)  # CC=8, fan=18
def map_cmd(project, output, force, stdout)  # CC=6, fan=12
def main()  # CC=4, fan=2
def main_sumr()  # CC=3, fan=2
```

### `sumd.parser` (`sumd/parser.py`)

```python
def parse(content)  # CC=1, fan=2
def parse_file(path)  # CC=1, fan=2
def validate(document)  # CC=1, fan=2
def _validate_yaml_body(body, path)  # CC=2, fan=1
def _validate_less_css_body(body, path)  # CC=2, fan=1
def _validate_mermaid_body(body, path)  # CC=2, fan=4
def _validate_toon_body(body, path)  # CC=2, fan=1
def _validate_bash_body(body, path)  # CC=4, fan=1
def _validate_deps_body(body, path)  # CC=5, fan=6
def validate_codeblocks(content, source)  # CC=13, fan=12 ⚠
def _check_h1(lines, source)  # CC=2, fan=2
def _check_required_sections(lines, source, profile)  # CC=1, fan=6
def _check_metadata_fields(lines, source)  # CC=7, fan=6
def _check_unclosed_fences(lines, source)  # CC=2, fan=2
def _check_empty_links(content, source)  # CC=1, fan=1
def validate_markdown(content, source, profile)  # CC=1, fan=6
def validate_sumd_file(path, profile)  # CC=2, fan=5
class SectionType:  # SUMD section types.
class Section:  # Represents a SUMD section.
class SUMDDocument:  # Represents a parsed SUMD document.
class SUMDParser:  # Parser for SUMD markdown documents.
    def __init__()  # CC=1
    def parse(content)  # CC=1
    def parse_file(path)  # CC=1
    def _parse_header(lines)  # CC=9
    def _parse_sections(lines)  # CC=6
    def validate(document)  # CC=5
class CodeBlockIssue:
```

### `sumd.mcp_server` (`sumd/mcp_server.py`)

```python
def _doc_to_dict(doc)  # CC=1, fan=0
def _resolve_path(path)  # CC=2, fan=3
def list_tools()  # CC=1, fan=2
def _tool_parse_sumd(arguments)  # CC=1, fan=5
def _tool_validate_sumd(arguments)  # CC=1, fan=7
def _tool_export_sumd(arguments)  # CC=5, fan=8
def _tool_list_sections(arguments)  # CC=1, fan=4
def _tool_get_section(arguments)  # CC=3, fan=6
def _tool_info_sumd(arguments)  # CC=1, fan=5
def _tool_generate_sumd(arguments)  # CC=5, fan=5
def call_tool(name, arguments)  # CC=3, fan=4
def main()  # CC=2, fan=3
```

## Call Graph

*130 nodes · 119 edges · 20 modules · CC̄=4.5*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `generate_map_toon` *(in sumd.extractor)* | 11 ⚠ | 1 | 32 | **33** |
| `analyze` *(in sumd.cli)* | 11 ⚠ | 0 | 33 | **33** |
| `_render_call_graph` *(in sumd.renderer)* | 7 | 1 | 28 | **29** |
| `_collect` *(in sumd.pipeline.RenderPipeline)* | 3 | 0 | 28 | **28** |
| `_render_api_stubs` *(in sumd.renderer)* | 11 ⚠ | 1 | 27 | **28** |
| `_run_analysis_tools` *(in sumd.cli)* | 11 ⚠ | 1 | 27 | **28** |
| `validate_codeblocks` *(in sumd.parser)* | 13 ⚠ | 1 | 25 | **26** |
| `extract_openapi` *(in sumd.extractor)* | 12 ⚠ | 1 | 24 | **25** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 130 | edges: 119 | modules: 20
# CC̄=4.5

HUBS[20]:
  sumd.extractor.generate_map_toon
    CC=11  in:1  out:32  total:33
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.renderer._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:28  total:28
  sumd.renderer._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.cli._run_analysis_tools
    CC=11  in:1  out:27  total:28
  sumd.parser.validate_codeblocks
    CC=13  in:1  out:25  total:26
  sumd.extractor.extract_openapi
    CC=12  in:1  out:24  total:25
  sumd.renderer._render_extras
    CC=11  in:1  out:21  total:22
  sumd.renderer._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.cli._scan_one_project
    CC=12  in:1  out:21  total:22
  sumd.renderer._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.renderer._collect_pkg_sources
    CC=14  in:1  out:19  total:20
  sumd.renderer._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.renderer._parse_calls_hubs
    CC=15  in:1  out:18  total:19
  sumd.renderer._render_workflows_taskfile
    CC=6  in:1  out:17  total:18

MODULES:
  sumd.cli  [22 funcs]
    _api_scenario_template  CC=1  out:3
    _export_sumd_json  CC=2  out:2
    _lint_collect_paths  CC=6  out:7
    _render_write_validate  CC=5  out:5
    _run_analysis_tools  CC=11  out:27
    _scaffold_crud_scenarios  CC=5  out:7
    _scaffold_from_openapi  CC=7  out:14
    _scaffold_generic  CC=1  out:3
    _scaffold_smoke_scenario  CC=6  out:5
    _scaffold_write  CC=3  out:4
  sumd.extractor  [26 funcs]
    _analyse_py_module  CC=2  out:6
    _analyse_py_top_classes  CC=11  out:14
    _analyse_py_top_funcs  CC=5  out:7
    _cc_estimate  CC=4  out:4
    _collect_map_files  CC=7  out:12
    _fan_out  CC=5  out:8
    _lang_of  CC=1  out:2
    _map_cc_stats  CC=12  out:13
    _parse_doql_content  CC=6  out:19
    _parse_doql_entities  CC=4  out:8
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
  sumd.parser  [10 funcs]
    parse_file  CC=1  out:2
    _check_empty_links  CC=2  out:1
    _check_h1  CC=3  out:2
    _check_metadata_fields  CC=9  out:7
    _check_required_sections  CC=7  out:6
    _check_unclosed_fences  CC=4  out:2
    validate  CC=1  out:2
    validate_codeblocks  CC=13  out:25
    validate_markdown  CC=1  out:6
    validate_sumd_file  CC=3  out:5
  sumd.pipeline  [2 funcs]
    _collect  CC=3  out:28
    run  CC=2  out:3
  sumd.renderer  [41 funcs]
    _collect_infra_sources  CC=6  out:10
    _collect_pkg_sources  CC=14  out:19
    _collect_sources  CC=1  out:2
    _inject_toc  CC=3  out:9
    _parse_calls_header  CC=6  out:12
    _parse_calls_hubs  CC=15  out:18
    _parse_calls_toon  CC=1  out:3
    _render_api_stubs  CC=11  out:27
    _render_architecture  CC=6  out:12
    _render_architecture_doql_parsed  CC=1  out:4
  sumd.sections.api_stubs  [1 funcs]
    render  CC=1  out:1
  sumd.sections.architecture  [1 funcs]
    render  CC=1  out:1
  sumd.sections.call_graph  [1 funcs]
    render  CC=1  out:1
  sumd.sections.code_analysis  [1 funcs]
    render  CC=1  out:1
  sumd.sections.configuration  [1 funcs]
    render  CC=1  out:1
  sumd.sections.dependencies  [1 funcs]
    render  CC=1  out:1
  sumd.sections.deployment  [1 funcs]
    render  CC=1  out:1
  sumd.sections.environment  [1 funcs]
    render  CC=1  out:4
  sumd.sections.extras  [1 funcs]
    render  CC=1  out:1
  sumd.sections.interfaces  [1 funcs]
    render  CC=1  out:1
  sumd.sections.quality  [1 funcs]
    render  CC=1  out:1
  sumd.sections.source_snippets  [1 funcs]
    render  CC=1  out:1
  sumd.sections.workflows  [1 funcs]
    render  CC=1  out:1
  sumd.toon_parser  [7 funcs]
    _parse_toon_block_api  CC=6  out:4
    _parse_toon_block_assert  CC=7  out:9
    _parse_toon_block_config  CC=9  out:8
    _parse_toon_block_navigate  CC=7  out:5
    _parse_toon_block_performance  CC=7  out:8
    _parse_toon_file  CC=4  out:16
    extract_testql_scenarios  CC=7  out:12

EDGES:
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_config
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_api
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_assert
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_performance
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_navigate
  sumd.toon_parser.extract_testql_scenarios → sumd.toon_parser._parse_toon_file
  sumd.extractor.extract_pyproject → sumd.extractor._read_toml
  sumd.extractor._parse_doql_content → sumd.extractor._parse_doql_interfaces
  sumd.extractor._parse_doql_content → sumd.extractor._parse_doql_entities
  sumd.extractor._parse_doql_content → sumd.extractor._parse_doql_workflows
  sumd.extractor.extract_doql → sumd.extractor._parse_doql_content
  sumd.extractor._analyse_py_top_funcs → sumd.extractor._fan_out
  sumd.extractor._analyse_py_top_funcs → sumd.extractor._cc_estimate
  sumd.extractor._analyse_py_top_classes → sumd.extractor._fan_out
  sumd.extractor._analyse_py_module → sumd.extractor._try_radon_cc
  sumd.extractor._analyse_py_module → sumd.extractor._analyse_py_top_funcs
  sumd.extractor._analyse_py_module → sumd.extractor._analyse_py_top_classes
  sumd.extractor._collect_map_files → sumd.extractor._lang_of
  sumd.extractor._render_map_detail → sumd.extractor._analyse_py_module
  sumd.extractor.generate_map_toon → sumd.extractor._collect_map_files
  sumd.extractor.generate_map_toon → sumd.extractor._render_map_detail
  sumd.extractor.generate_map_toon → sumd.extractor._map_cc_stats
  sumd.extractor.extract_source_snippets → sumd.extractor._analyse_py_module
  sumd.cli.validate → sumd.parser.SUMDParser.parse_file
  sumd.cli.validate → sumd.parser.validate
  sumd.cli.export → sumd.parser.SUMDParser.parse_file
  sumd.cli.info → sumd.parser.SUMDParser.parse_file
  sumd.cli.extract → sumd.parser.SUMDParser.parse_file
  sumd.cli._render_write_validate → sumd.parser.validate_sumd_file
  sumd.cli._render_write_validate → sumd.parser.SUMDParser.parse_file
  sumd.cli._scan_one_project → sumd.cli._render_write_validate
  sumd.cli._scan_one_project → sumd.cli._export_sumd_json
  sumd.cli._scan_one_project → sumd.cli._run_analysis_tools
  sumd.cli.lint → sumd.cli._lint_collect_paths
  sumd.cli.lint → sumd.parser.validate_sumd_file
  sumd.cli.analyze → sumd.cli._setup_tools_venv
  sumd.cli._scaffold_smoke_scenario → sumd.cli._scaffold_write
  sumd.cli._scaffold_smoke_scenario → sumd.cli._api_scenario_template
  sumd.cli._scaffold_crud_scenarios → sumd.cli._scaffold_write
  sumd.cli._scaffold_crud_scenarios → sumd.cli._api_scenario_template
  sumd.cli._scaffold_from_openapi → sumd.cli._scaffold_smoke_scenario
  sumd.cli._scaffold_from_openapi → sumd.cli._scaffold_crud_scenarios
  sumd.cli._scaffold_generic → sumd.cli._api_scenario_template
  sumd.cli._scaffold_generic → sumd.cli._scaffold_write
  sumd.cli.map_cmd → sumd.extractor.generate_map_toon
  sumd.cli.main → sumd.cli.cli
  sumd.cli.main_sumr → sumd.cli.cli
  sumd.pipeline.RenderPipeline._collect → sumd.extractor.extract_pyproject
  sumd.pipeline.RenderPipeline._collect → sumd.extractor.extract_taskfile
  sumd.pipeline.RenderPipeline._collect → sumd.toon_parser.extract_testql_scenarios
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Smoke (1)

**`smoke-generic.testql.toon.yaml — smoke tests for sumd CLI`**
- `GET /health` → `200`
- assert `status < 500`

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation
