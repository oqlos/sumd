# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `sumd`
- **version**: `0.3.4`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), pyqual.yaml, goal.yaml, .env.example, src(8 mod), project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
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

## Dependencies

### Runtime

```text markpact:deps python
click>=8.0
pyyaml>=6.0
toml>=0.10.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-cov>=4.0
ruff>=0.1
build
twine
pyqual>=0.1
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
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
def required_tools_for_profile(profile)  # CC=1, fan=0
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
def _run_analysis_tools(proj_dir, tool_list, skip_tools)  # CC=12, fan=5 ⚠
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

*133 nodes · 121 edges · 20 modules · CC̄=4.6*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `generate_map_toon` *(in sumd.extractor)* | 11 ⚠ | 2 | 32 | **34** |
| `analyze` *(in sumd.cli)* | 11 ⚠ | 0 | 33 | **33** |
| `_collect` *(in sumd.pipeline.RenderPipeline)* | 3 | 0 | 30 | **30** |
| `_run_analysis_tools` *(in sumd.cli)* | 15 ⚠ | 1 | 28 | **29** |
| `_render_call_graph` *(in sumd.renderer)* | 7 | 1 | 28 | **29** |
| `_render_api_stubs` *(in sumd.renderer)* | 11 ⚠ | 1 | 27 | **28** |
| `validate_codeblocks` *(in sumd.parser)* | 13 ⚠ | 1 | 25 | **26** |
| `extract_openapi` *(in sumd.extractor)* | 12 ⚠ | 1 | 24 | **25** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 133 | edges: 121 | modules: 20
# CC̄=4.6

HUBS[20]:
  sumd.extractor.generate_map_toon
    CC=11  in:2  out:32  total:34
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:30  total:30
  sumd.cli._run_analysis_tools
    CC=15  in:1  out:28  total:29
  sumd.renderer._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.renderer._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.parser.validate_codeblocks
    CC=13  in:1  out:25  total:26
  sumd.extractor.extract_openapi
    CC=12  in:1  out:24  total:25
  sumd.pipeline._refresh_analysis_files
    CC=11  in:1  out:23  total:24
  sumd.renderer._render_extras
    CC=11  in:1  out:21  total:22
  sumd.renderer._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.cli._scan_one_project
    CC=12  in:1  out:21  total:22
  sumd.renderer._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.renderer._collect_pkg_sources
    CC=14  in:1  out:19  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.renderer._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.renderer._parse_calls_hubs
    CC=15  in:1  out:18  total:19

MODULES:
  sumd.cli  [22 funcs]
    _api_scenario_template  CC=1  out:3
    _export_sumd_json  CC=2  out:2
    _lint_collect_paths  CC=6  out:7
    _render_write_validate  CC=5  out:5
    _run_analysis_tools  CC=15  out:28
    _scaffold_crud_scenarios  CC=5  out:7
    _scaffold_from_openapi  CC=7  out:14
    _scaffold_generic  CC=1  out:3
    _scaffold_smoke_scenario  CC=6  out:5
    _scaffold_write  CC=3  out:4
  sumd.extractor  [27 funcs]
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
  sumd.pipeline  [4 funcs]
    _collect  CC=3  out:30
    run  CC=2  out:3
    _refresh_analysis_files  CC=11  out:23
    _refresh_map_toon  CC=3  out:3
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
  sumd.pipeline._refresh_map_toon → sumd.extractor.generate_map_toon
  sumd.pipeline._refresh_analysis_files → sumd.extractor.required_tools_for_profile
  sumd.pipeline.RenderPipeline._collect → sumd.extractor.extract_pyproject
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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 133 | edges: 121 | modules: 20
# CC̄=4.6

HUBS[20]:
  sumd.extractor.generate_map_toon
    CC=11  in:2  out:32  total:34
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:30  total:30
  sumd.cli._run_analysis_tools
    CC=15  in:1  out:28  total:29
  sumd.renderer._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.renderer._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.parser.validate_codeblocks
    CC=13  in:1  out:25  total:26
  sumd.extractor.extract_openapi
    CC=12  in:1  out:24  total:25
  sumd.pipeline._refresh_analysis_files
    CC=11  in:1  out:23  total:24
  sumd.renderer._render_extras
    CC=11  in:1  out:21  total:22
  sumd.renderer._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.cli._scan_one_project
    CC=12  in:1  out:21  total:22
  sumd.renderer._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.renderer._collect_pkg_sources
    CC=14  in:1  out:19  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.renderer._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.renderer._parse_calls_hubs
    CC=15  in:1  out:18  total:19

MODULES:
  sumd.cli  [22 funcs]
    _api_scenario_template  CC=1  out:3
    _export_sumd_json  CC=2  out:2
    _lint_collect_paths  CC=6  out:7
    _render_write_validate  CC=5  out:5
    _run_analysis_tools  CC=15  out:28
    _scaffold_crud_scenarios  CC=5  out:7
    _scaffold_from_openapi  CC=7  out:14
    _scaffold_generic  CC=1  out:3
    _scaffold_smoke_scenario  CC=6  out:5
    _scaffold_write  CC=3  out:4
  sumd.extractor  [27 funcs]
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
  sumd.pipeline  [4 funcs]
    _collect  CC=3  out:30
    run  CC=2  out:3
    _refresh_analysis_files  CC=11  out:23
    _refresh_map_toon  CC=3  out:3
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
  sumd.pipeline._refresh_map_toon → sumd.extractor.generate_map_toon
  sumd.pipeline._refresh_analysis_files → sumd.extractor.required_tools_for_profile
  sumd.pipeline.RenderPipeline._collect → sumd.extractor.extract_pyproject
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 28f 5130L | python:26,shell:2 | 2026-04-19
# CC̄=4.6 | critical:2/198 | dups:0 | cycles:0

HEALTH[3]:
  🔴 GOD   sumd/parser.py = 543L, 5 classes, 23m, max CC=13
  🟡 CC    _run_analysis_tools CC=15 (limit:15)
  🟡 CC    _parse_calls_hubs CC=15 (limit:15)

REFACTOR[2]:
  1. split sumd/parser.py  (god module)
  2. split 2 high-CC methods  (CC>15)

PIPELINES[72]:
  [1] Src [main]: main → ask → build_context → parse_file
      PURITY: 100% pure
  [2] Src [main]: main → ask → parse_file
      PURITY: 100% pure
  [3] Src [main]: main → run
      PURITY: 100% pure
  [4] Src [validate]: validate → parse_file
      PURITY: 100% pure
  [5] Src [export]: export → parse_file
      PURITY: 100% pure

LAYERS:
  sumd/                           CC̄=4.6    ←in:14  →out:0
  │ !! cli                       1090L  0C   29m  CC=15     ←0
  │ !! renderer                   989L  0C   46m  CC=15     ←14
  │ !! extractor                  886L  0C   33m  CC=13     ←2
  │ !! parser                     543L  5C   23m  CC=13     ←4
  │ mcp_server                 358L  0C   12m  CC=5      ←0
  │ pipeline                   318L  1C    8m  CC=11     ←0
  │ toon_parser                173L  0C    8m  CC=9      ←1
  │ __init__                   103L  0C    0m  CC=0.0    ←0
  │ base                        93L  2C    2m  CC=1      ←0
  │ refactor_analysis           68L  1C    2m  CC=3      ←0
  │ metadata                    51L  1C    2m  CC=5      ←0
  │ __init__                    33L  0C    0m  CC=0.0    ←0
  │ call_graph                  27L  1C    2m  CC=2      ←0
  │ dependencies                26L  1C    2m  CC=4      ←0
  │ source_snippets             26L  1C    2m  CC=1      ←0
  │ code_analysis               25L  1C    2m  CC=3      ←0
  │ api_stubs                   25L  1C    2m  CC=1      ←0
  │ environment                 24L  1C    2m  CC=2      ←0
  │ interfaces                  23L  1C    2m  CC=3      ←0
  │ deployment                  23L  1C    2m  CC=1      ←0
  │ architecture                23L  1C    2m  CC=1      ←0
  │ quality                     21L  1C    2m  CC=1      ←0
  │ workflows                   21L  1C    2m  CC=2      ←0
  │ extras                      21L  1C    2m  CC=2      ←0
  │ configuration               21L  1C    2m  CC=1      ←0
  │ generator                   15L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ project.sh                  35L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ bootstrap.sh                69L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                          sumd  sumd.sections
           sumd             ──            ←14  hub
  sumd.sections             14             ──  !! fan-out
  CYCLES: none
  HUB: sumd/ (fan-in=14)
  SMELL: sumd.sections/ fan-out=14 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 28f 5288L | 2026-04-19

SUMMARY:
  files_scanned: 28
  total_lines:   5288
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   25
  scan_ms:       19151

HOTSPOTS[2] (files with most duplication):
  sumd/toon_parser.py  dup=28L  groups=1  frags=2  (0.5%)
  sumd/parser.py  dup=22L  groups=1  frags=2  (0.4%)

DUPLICATES[2] (ranked by impact):
  [ec6388d8055c3e57]   STRU  _parse_toon_block_performance  L=14 N=2 saved=14 sim=1.00
      sumd/toon_parser.py:70-83  (_parse_toon_block_performance)
      sumd/toon_parser.py:102-115  (_parse_toon_block_gui)
  [d1ab1a804f1b435b]   STRU  parse  L=11 N=2 saved=11 sim=1.00
      sumd/parser.py:188-198  (parse)
      sumd/parser.py:201-211  (parse_file)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → sumd/utils/_parse_toon_block_performance.py
      WHY: 2 occurrences of 14-line block across 1 files — saves 14 lines
      FILES: sumd/toon_parser.py
  [2] ○ extract_function   → sumd/utils/parse.py
      WHY: 2 occurrences of 11-line block across 1 files — saves 11 lines
      FILES: sumd/parser.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=14L  → sumd/utils/_parse_toon_block_performance.py
      FILES: toon_parser.py
  [2] extract_function   saved=11L  → sumd/utils/parse.py
      FILES: parser.py

EFFORT_ESTIMATE (total ≈ 0.8h):
  easy   _parse_toon_block_performance       saved=14L  ~28min
  easy   parse                               saved=11L  ~22min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 25 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 191 func | 23f | 2026-04-19

NEXT[5] (ranked by impact):
  [1] !! SPLIT           sumd/cli.py
      WHY: 1090L, 0 classes, max CC=15
      EFFORT: ~4h  IMPACT: 16350

  [2] !! SPLIT           sumd/renderer.py
      WHY: 989L, 0 classes, max CC=15
      EFFORT: ~4h  IMPACT: 14835

  [3] !! SPLIT           sumd/extractor.py
      WHY: 886L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 11518

  [4] !  SPLIT-FUNC      _run_analysis_tools  CC=15  fan=9
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 135

  [5] !  SPLIT-FUNC      _parse_calls_hubs  CC=15  fan=7
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 105


RISKS[3]:
  ⚠ Splitting sumd/cli.py may break 29 import paths
  ⚠ Splitting sumd/renderer.py may break 46 import paths
  ⚠ Splitting sumd/extractor.py may break 33 import paths

METRICS-TARGET:
  CC̄:          4.6 → ≤3.2
  max-CC:      15 → ≤7
  god-modules: 4 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.5 → now CC̄=4.6
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 92f | 53✓ 1⚠ 7✗ | 2026-04-19

SUMMARY:
  scanned: 92  passed: 53 (57.6%)  warnings: 1  errors: 7  unsupported: 32

WARNINGS[1]{path,score}:
  /home/tom/github/oqlos/sumd/sumd/renderer.py,0.98
    issues[1]{rule,severity,message,line}:
      complexity.maintainability,warning,Low maintainability index: 0.0 (threshold: 20),

ERRORS[7]{path,score}:
  /home/tom/github/oqlos/sumd/sumd/mcp_server.py,0.86
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.stdio' not found,20
      python.import.resolvable,error,Module 'mcp.types' not found,21
      python.import.resolvable,error,Module 'mcp.server' not found,22
      python.import.resolvable,error,Module 'toml' not found,227
  /home/tom/github/oqlos/sumd/tests/test_cli.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,7
  /home/tom/github/oqlos/sumd/tests/test_dogfood.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,17
  /home/tom/github/oqlos/sumd/tests/test_pipeline.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,7
  /home/tom/github/oqlos/sumd/sumd/cli.py,0.96
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toml' not found,156
      python.import.resolvable,error,Module 'toml' not found,94
  /home/tom/github/oqlos/sumd/sumd/extractor.py,0.96
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toml' not found,25
  /home/tom/github/oqlos/sumd/tests/test_mcp_server.py,0.96
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,8

UNSUPPORTED[5]{bucket,count}:
  *.md,18
  Dockerfile*,1
  *.txt,1
  *.yml,5
  other,7
```

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation
