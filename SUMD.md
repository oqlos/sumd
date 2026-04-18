# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Contents

- [Metadata](#metadata)
- [Intent](#intent)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)

## Metadata

- **name**: `sumd`
- **version**: `0.1.16`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(1), app.doql.css, goal.yaml, .env.example, src(7 mod), project/(2 analysis files)

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.css`)

```css markpact:file path=app.doql.css
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
- `sumd.renderer`
- `sumd.toon_parser`

## Interfaces

### CLI Entry Points

- `sumd`
- `sumd-mcp`

### testql Scenarios

#### `testql-scenarios/smoke-generic.testql.toon.yaml`

```toon markpact:file path=testql-scenarios/smoke-generic.testql.toon.yaml
# SCENARIO: smoke-generic.testql.toon.yaml — smoke generic
# TYPE: smoke
# VERSION: 1.0
# GENERATED: true

# ── Konfiguracja ──────────────────────────────────────
CONFIG[1]{key, value}:
  base_path,  /api/v1  # TODO: adjust base_path

# ── Wywołania API ─────────────────────────────────────
API[2]{method, endpoint, status}:
  GET,  /health,  200  # TODO: adjust
  GET,  /,  200       # TODO: adjust
# ── Asercje ───────────────────────────────────────────
# ASSERT[0]{field, op, expected}:
#   TODO: fill in assertions
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:file path=Taskfile.yml
# Taskfile.yml — sumd (Structured Unified Markdown Descriptor) project runner
# https://taskfile.dev

version: "3"

vars:
  APP_NAME: sumd
  DOQL_OUTPUT: app.doql.less
  DOQL_CMD: "{{if eq OS \"windows\"}}doql.exe{{else}}doql{{end}}"

env:
  PYTHONPATH: "{{.PWD}}"

tasks:
  # ─────────────────────────────────────────────────────────────────────────────
  # Development
  # ─────────────────────────────────────────────────────────────────────────────

  install:
    desc: Install Python dependencies (editable)
    cmds:
      - pip install -e .[dev]

  quality:
    desc: Run pyqual quality pipeline
    cmds:
      - pyqual run

  quality:fix:
    desc: Run pyqual with auto-fix
    cmds:
      - pyqual run --fix

  quality:report:
    desc: Generate pyqual quality report
    cmds:
      - pyqual report

  test:
    desc: Run pytest suite
    cmds:
      - pytest -q

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
      - python -m build

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
    desc: Generate project structure (app.doql.css + app.doql.less)
    cmds:
      - |
        echo "📁 Analyzing sumd project structure..."
        {{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force
        echo "🎨 Exporting to LESS format..."
        {{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}
        echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}"

  doql:adopt:
    desc: Reverse-engineer sumd project structure (CSS only)
    cmds:
      - "{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.css --force"
      - echo "✅ Captured in app.doql.css"

  doql:export:
    desc: Export to LESS format
    cmds:
      - |
        if [ ! -f "app.doql.css" ]; then
          echo "❌ app.doql.css not found. Run: task structure"
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
      - |
        # Regenerate LESS from CSS if CSS exists
        if [ -f "app.doql.css" ]; then
          {{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}
        fi
      - "{{.DOQL_CMD}} build app.doql.css --out build/"

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
      - python -m sumd.cli docs/ docs/

  # ─────────────────────────────────────────────────────────────────────────────
  # Utility
  # ─────────────────────────────────────────────────────────────────────────────

  help:
    desc: Show available tasks
    cmds:
      - task --list
```

## Configuration

```yaml
project:
  name: sumd
  version: 0.1.16
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
click>=8.0
pyyaml>=6.0
toml>=0.10.0
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

```toon markpact:file path=project/map.toon.yaml
# sumd | 10f 3151L | shell:1,python:9 | 2026-04-18
# stats: 104 func | 0 cls | 10 mod | CC̄=6.5 | critical:10 | cycles:0
# alerts[5]: fan-out generate_sumd_content=34; fan-out _scaffold_from_openapi=20; fan-out call_tool=20; CC call_tool=24; CC generate_map_toon=22
# hotspots[5]: generate_sumd_content fan=34; _scaffold_from_openapi fan=20; call_tool fan=20; scaffold fan=19; generate fan=17
# evolution: CC̄ 6.5→6.5 (flat 0.0)
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[10]:
  project.sh,35
  scripts/generate_all_sumd.py,20
  sumd/__init__.py,33
  sumd/cli.py,742
  sumd/extractor.py,707
  sumd/generator.py,17
  sumd/mcp_server.py,321
  sumd/parser.py,476
  sumd/renderer.py,634
  sumd/toon_parser.py,166
D:
  sumd/mcp_server.py:
    e: _doc_to_dict,_resolve_path,list_tools,call_tool,main
    _doc_to_dict(doc)
    _resolve_path(path)
    list_tools()
    call_tool(name;arguments)
    main()
  sumd/extractor.py:
    e: _read_toml,extract_pyproject,extract_taskfile,extract_openapi,_parse_doql_entities,_parse_doql_interfaces,_parse_doql_workflows,_parse_doql_content,extract_doql,extract_pyqual,extract_python_modules,extract_readme_title,extract_requirements,extract_makefile,extract_goal,extract_env,extract_dockerfile,extract_docker_compose,extract_package_json,_lang_of,_fan_out,_cc_estimate,_try_radon_cc,_analyse_py_module,_collect_map_files,_render_map_detail,generate_map_toon,extract_project_analysis
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
    _analyse_py_module(path)
    _collect_map_files(proj_dir)
    _render_map_detail(proj_dir;modules)
    generate_map_toon(proj_dir)
    extract_project_analysis(proj_dir)
  sumd/renderer.py:
    e: _render_architecture,_render_architecture_doql_parsed,_render_interfaces,_render_interfaces_openapi,_render_interfaces_testql,_render_workflows,_render_quality,_render_dependencies,_render_deployment,_render_extras,_render_code_analysis,_collect_sources,_render_metadata_section,_render_configuration_section,_render_env_section,_render_goal_section,_inject_toc,generate_sumd_content
    _render_architecture(doql;modules;name;proj_dir;raw_sources)
    _render_architecture_doql_parsed(doql;L)
    _render_interfaces(scripts;openapi;scenarios;proj_dir;raw_sources)
    _render_interfaces_openapi(openapi;proj_dir;raw_sources;L)
    _render_interfaces_testql(scenarios;proj_dir;raw_sources;L)
    _render_workflows(doql;tasks;proj_dir;raw_sources)
    _render_quality(pyqual;proj_dir;raw_sources)
    _render_dependencies(deps;dev_deps)
    _render_deployment(pkg_json;name;reqs;dockerfile;compose)
    _render_extras(makefile;pkg_json)
    _render_code_analysis(project_analysis)
    _collect_sources(pyproj;reqs;tasks;makefile;scenarios;openapi;doql;pyqual;goal;env_vars;dockerfile;compose;pkg_json;modules;project_analysis)
    _render_metadata_section(name;version;py_req;license_;ai_model;openapi;sources_used)
    _render_configuration_section(name;version)
    _render_env_section(env_vars)
    _render_goal_section(goal)
    _inject_toc(content)
    generate_sumd_content(proj_dir;return_sources;raw_sources)
  sumd/cli.py:
    e: cli,validate,export,info,generate,extract,_detect_projects,_run_analysis_tools,_scan_one_project,scan,lint,_setup_tools_venv,_run_code2llm_formats,_run_tool_subprocess,analyze,_api_scenario_template,_scaffold_write,_scaffold_from_openapi,_scaffold_generic,scaffold,map_cmd,main
    cli()
    validate(file)
    export(file;format;output)
    info(file)
    generate(file;format;output)
    extract(file;section)
    _detect_projects(workspace)
    _run_analysis_tools(proj_dir;tool_list)
    _scan_one_project(proj_dir;fix;raw;export_json;run_analyze;tool_list;parser_inst)
    scan(workspace;export_json;report;fix;raw;analyze;tools)
    lint(files;workspace;as_json)
    _setup_tools_venv(venv_dir;tool_list;force)
    _run_code2llm_formats(bin_dir;project;project_output)
    _run_tool_subprocess(bin_dir;tool;cmd_args)
    analyze(project;tools;force)
    _api_scenario_template(name;scenario_type;endpoints_block;base_path)
    _scaffold_write(path;content;force;generated;skipped)
    _scaffold_from_openapi(spec;out_dir;scenario_type;force;generated;skipped)
    _scaffold_generic(out_dir;force;generated;skipped)
    scaffold(project;output;force;scenario_type)
    map_cmd(project;output;force;stdout)
    main()
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
    _check_required_sections(lines;source)
    _check_metadata_fields(lines;source)
    _check_unclosed_fences(lines;source)
    _check_empty_links(content;source)
    validate_markdown(content;source)
    validate_sumd_file(path)
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
  project.sh:
  sumd/__init__.py:
  sumd/generator.py:
  scripts/generate_all_sumd.py:
```

### `project/calls.toon.yaml`

```toon markpact:file path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 59 | edges: 55 | modules: 6
# CC̄=6.5

HUBS[20]:
  sumd.mcp_server.call_tool
    CC=24  in:0  out:64  total:64
  sumd.renderer.generate_sumd_content
    CC=4  in:1  out:60  total:61
  sumd.extractor.generate_map_toon
    CC=22  in:1  out:44  total:45
  sumd.renderer._render_interfaces_testql
    CC=20  in:1  out:37  total:38
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.cli._scan_one_project
    CC=16  in:1  out:25  total:26
  sumd.parser.validate_codeblocks
    CC=13  in:1  out:25  total:26
  sumd.extractor.extract_openapi
    CC=12  in:1  out:24  total:25
  sumd.extractor._analyse_py_module
    CC=15  in:1  out:24  total:25
  sumd.cli._scaffold_from_openapi
    CC=16  in:1  out:24  total:25
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.renderer._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.extractor.extract_pyproject
    CC=3  in:1  out:17  total:18
  sumd.toon_parser._parse_toon_file
    CC=4  in:1  out:16  total:17
  sumd.cli.export
    CC=8  in:0  out:16  total:16
  sumd.extractor.extract_taskfile
    CC=10  in:1  out:13  total:14
  sumd.cli._setup_tools_venv
    CC=7  in:1  out:13  total:14
  sumd.toon_parser.extract_testql_scenarios
    CC=7  in:1  out:12  total:13

MODULES:
  sumd.cli  [14 funcs]
    _api_scenario_template  CC=1  out:3
    _scaffold_from_openapi  CC=16  out:24
    _scaffold_generic  CC=1  out:3
    _scaffold_write  CC=3  out:4
    _scan_one_project  CC=16  out:25
    _setup_tools_venv  CC=7  out:13
    analyze  CC=11  out:33
    cli  CC=1  out:2
    export  CC=8  out:16
    extract  CC=5  out:13
  sumd.extractor  [21 funcs]
    _analyse_py_module  CC=15  out:24
    _collect_map_files  CC=7  out:12
    _fan_out  CC=5  out:8
    _lang_of  CC=1  out:2
    _parse_doql_content  CC=6  out:19
    _parse_doql_entities  CC=4  out:8
    _parse_doql_interfaces  CC=3  out:10
    _parse_doql_workflows  CC=7  out:18
    _read_toml  CC=2  out:4
    _render_map_detail  CC=5  out:6
  sumd.mcp_server  [3 funcs]
    _doc_to_dict  CC=2  out:0
    _resolve_path  CC=2  out:4
    call_tool  CC=24  out:64
  sumd.parser  [10 funcs]
    parse_file  CC=1  out:2
    _check_empty_links  CC=2  out:1
    _check_h1  CC=3  out:2
    _check_metadata_fields  CC=9  out:7
    _check_required_sections  CC=6  out:6
    _check_unclosed_fences  CC=4  out:2
    validate  CC=1  out:2
    validate_codeblocks  CC=13  out:25
    validate_markdown  CC=1  out:6
    validate_sumd_file  CC=3  out:5
  sumd.renderer  [4 funcs]
    _render_interfaces  CC=5  out:9
    _render_interfaces_openapi  CC=6  out:19
    _render_interfaces_testql  CC=20  out:37
    generate_sumd_content  CC=4  out:60
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
  sumd.extractor._analyse_py_module → sumd.extractor._try_radon_cc
  sumd.extractor._analyse_py_module → sumd.extractor._fan_out
  sumd.extractor._collect_map_files → sumd.extractor._lang_of
  sumd.extractor._render_map_detail → sumd.extractor._analyse_py_module
  sumd.extractor.generate_map_toon → sumd.extractor._collect_map_files
  sumd.extractor.generate_map_toon → sumd.extractor._render_map_detail
  sumd.mcp_server.call_tool → sumd.mcp_server._resolve_path
  sumd.mcp_server.call_tool → sumd.parser.SUMDParser.parse_file
  sumd.mcp_server.call_tool → sumd.mcp_server._doc_to_dict
  sumd.mcp_server.call_tool → sumd.parser.validate
  sumd.renderer._render_interfaces → sumd.renderer._render_interfaces_openapi
  sumd.renderer._render_interfaces → sumd.renderer._render_interfaces_testql
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_pyproject
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_taskfile
  sumd.renderer.generate_sumd_content → sumd.toon_parser.extract_testql_scenarios
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_openapi
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_doql
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_pyqual
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_python_modules
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_readme_title
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_requirements
  sumd.renderer.generate_sumd_content → sumd.extractor.extract_makefile
  sumd.cli.validate → sumd.parser.SUMDParser.parse_file
  sumd.cli.validate → sumd.parser.validate
  sumd.cli.export → sumd.parser.SUMDParser.parse_file
  sumd.cli.info → sumd.parser.SUMDParser.parse_file
  sumd.cli.extract → sumd.parser.SUMDParser.parse_file
  sumd.cli._scan_one_project → sumd.renderer.generate_sumd_content
  sumd.cli._scan_one_project → sumd.parser.validate_sumd_file
  sumd.cli._scan_one_project → sumd.parser.SUMDParser.parse_file
  sumd.cli.analyze → sumd.cli._setup_tools_venv
  sumd.cli._scaffold_from_openapi → sumd.cli._scaffold_write
  sumd.cli._scaffold_from_openapi → sumd.cli._api_scenario_template
  sumd.cli._scaffold_generic → sumd.cli._api_scenario_template
  sumd.cli._scaffold_generic → sumd.cli._scaffold_write
  sumd.cli.map_cmd → sumd.extractor.generate_map_toon
  sumd.cli.main → sumd.cli.cli
  sumd.parser.validate_markdown → sumd.parser._check_empty_links
  sumd.parser.validate_markdown → sumd.parser._check_unclosed_fences
```
