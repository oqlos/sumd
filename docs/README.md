<!-- code2docs:start --># sumd

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-770-green)
> **770** functions | **33** classes | **91** files | CC̄ = 4.3

> Auto-generated project documentation from source code analysis.

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

### CLI Usage

```bash
# Generate full documentation for your project
sumd ./my-project

# Only regenerate README
sumd ./my-project --readme-only

# Preview what would be generated (no file writes)
sumd ./my-project --dry-run

# Check documentation health
sumd check ./my-project

# Sync — regenerate only changed modules
sumd sync ./my-project
```

### Python API

```python
from sumd import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```




## Architecture

```
sumd/
├── SUMR
├── goal
├── SUMD
    ├── pre-commit-config
    ├── guards
├── pyqual
├── sumd/
├── pyproject
├── TODO
├── mcp
├── CHANGELOG
├── Taskfile
├── project
├── SPEC
├── README
    ├── USAGE
    ├── README
    ├── SUMD
    ├── sumd
    ├── README
        ├── anthropic_example
        ├── ollama_example
        ├── llm_cli_example
        ├── context_injection
        ├── openai_example
        ├── README
        ├── mcp_client
        ├── claude_desktop_config
        ├── continue_config
        ├── cursor_mcp
        ├── README
        ├── demo
        ├── README
            ├── goal
            ├── SUMD
            ├── sumd
            ├── pyproject
            ├── Taskfile
            ├── openapi
            ├── README
                    ├── toon
        ├── makefile
        ├── taskfile
        ├── vscode-tasks
        ├── docker-compose
        ├── pre-commit-config
        ├── github-actions
        ├── Dockerfile
        ├── README
    ├── toon_parser
    ├── cli
    ├── generator
    ├── extractor
    ├── parser
    ├── renderer
    ├── pipeline
    ├── mcp_server
        ├── base
        ├── interfaces
        ├── refactor_analysis
        ├── quality
        ├── deployment
        ├── code_analysis
        ├── metadata
    ├── sections/
        ├── dependencies
        ├── call_graph
        ├── architecture
        ├── source_snippets
        ├── workflows
        ├── extras
        ├── api_stubs
        ├── environment
        ├── configuration
    ├── bootstrap
        ├── toon
        ├── toon
            ├── toon
            ├── toon
            ├── toon
                ├── toon
    ├── prompt
    ├── README
        ├── toon
        ├── toon
        ├── toon
    ├── context
        ├── toon
    ├── calls
        ├── toon
```

## API Overview

### Classes

- **`SectionType`** — —
- **`Section`** — —
- **`SUMDDocument`** — —
- **`SUMDParser`** — —
- **`CodeBlockIssue`** — —
- **`SectionType`** — —
- **`Section`** — —
- **`SUMDDocument`** — —
- **`SUMDParser`** — —
- **`CodeBlockIssue`** — —
- **`SectionType`** — SUMD section types.
- **`Section`** — Represents a SUMD section.
- **`SUMDDocument`** — Represents a parsed SUMD document.
- **`SUMDParser`** — Parser for SUMD markdown documents.
- **`CodeBlockIssue`** — —
- **`RenderPipeline`** — Collect project data → build sections → render → inject TOC.
- **`RenderContext`** — All extracted data for a project, passed to every Section.render().
- **`Section`** — Protocol for all SUMD section renderers.
- **`InterfacesSection`** — —
- **`RefactorAnalysisSection`** — —
- **`QualitySection`** — —
- **`DeploymentSection`** — —
- **`CodeAnalysisSection`** — —
- **`MetadataSection`** — Render ## Metadata — always present, all profiles.
- **`DependenciesSection`** — —
- **`CallGraphSection`** — —
- **`ArchitectureSection`** — —
- **`SourceSnippetsSection`** — —
- **`WorkflowsSection`** — —
- **`ExtrasSection`** — —
- **`ApiStubsSection`** — —
- **`EnvironmentSection`** — —
- **`ConfigurationSection`** — —

### Functions

- `generate_sumd_content()` — —
- `extract_pyproject()` — —
- `extract_taskfile()` — —
- `extract_openapi()` — —
- `extract_doql()` — —
- `extract_pyqual()` — —
- `extract_python_modules()` — —
- `extract_readme_title()` — —
- `extract_requirements()` — —
- `extract_makefile()` — —
- `extract_goal()` — —
- `extract_env()` — —
- `extract_dockerfile()` — —
- `extract_docker_compose()` — —
- `extract_package_json()` — —
- `generate_map_toon()` — —
- `required_tools_for_profile()` — —
- `extract_source_snippets()` — —
- `extract_project_analysis()` — —
- `cli()` — —
- `validate()` — —
- `export()` — —
- `info()` — —
- `generate()` — —
- `extract()` — —
- `scan()` — —
- `lint()` — —
- `analyze()` — —
- `scaffold()` — —
- `map_cmd()` — —
- `main()` — —
- `main_sumr()` — —
- `parse()` — —
- `parse_file()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
- `list_tools()` — —
- `call_tool()` — —
- `ask()` — —
- `main()` — —
- `build_context()` — —
- `run()` — —
- `cli()` — —
- `validate()` — —
- `export()` — —
- `info()` — —
- `generate()` — —
- `extract()` — —
- `scan()` — —
- `lint()` — —
- `analyze()` — —
- `scaffold()` — —
- `map_cmd()` — —
- `main_sumr()` — —
- `extract_pyproject()` — —
- `extract_taskfile()` — —
- `extract_openapi()` — —
- `extract_doql()` — —
- `extract_pyqual()` — —
- `extract_python_modules()` — —
- `extract_readme_title()` — —
- `extract_requirements()` — —
- `extract_makefile()` — —
- `extract_goal()` — —
- `extract_env()` — —
- `extract_dockerfile()` — —
- `extract_docker_compose()` — —
- `extract_package_json()` — —
- `generate_map_toon()` — —
- `required_tools_for_profile()` — —
- `extract_source_snippets()` — —
- `extract_project_analysis()` — —
- `list_tools()` — —
- `call_tool()` — —
- `parse()` — —
- `parse_file()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
- `generate_sumd_content()` — —
- `extract_testql_scenarios()` — —
- `sumd_file()` — —
- `project_copy()` — —
- `test_sumd_scans_itself()` — —
- `test_sumd_scans_all_profiles()` — —
- `test_sumr_generates_sumr_md()` — —
- `test_sumd_lint_passes_on_generated_output()` — —
- `test_sumd_version_flag()` — —
- `test_sumd_scan_produces_no_unhandled_exceptions()` — —
- `test_parse_basic()` — —
- `test_parse_sections()` — —
- `test_validate_valid_document()` — —
- `test_validate_missing_intent()` — —
- `test_parse_file()` — —
- `test_parser_class()` — —
- `test_markpact_semantic_kinds_valid()` — —
- `test_markpact_unknown_kind_error()` — —
- `test_markpact_missing_path_error()` — —
- `proj_dir()` — —
- `test_pipeline_run_returns_string()` — —
- `test_pipeline_output_has_h1()` — —
- `test_pipeline_output_has_metadata()` — —
- `test_pipeline_return_sources()` — —
- `test_pipeline_profile_minimal()` — —
- `test_pipeline_profile_refactor()` — —
- `test_pipeline_with_modules()` — —
- `test_pipeline_with_taskfile()` — —
- `test_pipeline_with_dependencies()` — —
- `test_pipeline_injects_toc()` — —
- `test_required_tools_rich()` — —
- `test_required_tools_refactor()` — —
- `test_required_tools_minimal()` — —
- `test_refresh_map_toon_writes_file()` — —
- `test_refresh_analysis_files_noop_without_tools()` — —
- `make_ctx()` — —
- `test_placeholder()` — —
- `test_import()` — —
- `test_sumd_scans_itself()` — —
- `test_sumd_scans_all_profiles()` — —
- `test_sumr_generates_sumr_md()` — —
- `test_mcp_tools_registered()` — —
- `test_mcp_main_no_crash()` — —
- `print()` — —
- `print()` — —
- `generate_readme()` — —
- `ask(sumd_path, question, model)` — —
- `main()` — —
- `build_context(sumd_path)` — Return a focused context string from SUMD.md.
- `ask(sumd_path, question, model)` — —
- `main()` — —
- `run(sumd_file, single_tool, tool_args)` — —
- `main()` — —
- `extract_testql_scenarios(proj_dir)` — Scan all *.testql.toon.yaml and testql-scenarios/*.yaml files in project.
- `cli()` — SUMD - Structured Unified Markdown Descriptor CLI.
- `validate(file)` — Validate a SUMD document.
- `export(file, format, output)` — Export a SUMD document to structured format.
- `info(file)` — Display information about a SUMD document.
- `generate(file, format, output)` — Generate a SUMD document from structured format.
- `extract(file, section)` — Extract content from a SUMD document.
- `scan(workspace, export_json, report, fix)` — Scan a workspace directory and generate SUMD.md for every project found.
- `lint(files, workspace, as_json)` — Validate SUMD.md files — check markdown structure and codeblock formats.
- `analyze(project, tools, force)` — Run analysis tools (code2llm, redup, vallm) on a project.
- `scaffold(project, output, force, scenario_type)` — Generate testql scenario scaffolds from OpenAPI spec or SUMD.md.
- `map_cmd(project, output, force, stdout)` — Generate project/map.toon.yaml — static code map in toon format.
- `main()` — Main entry point — if first arg is a path, run 'scan <path> --fix'.
- `main_sumr()` — Entry point for `sumr` command — generates SUMR.md (refactor profile).
- `extract_pyproject(proj_dir)` — —
- `extract_taskfile(proj_dir)` — —
- `extract_openapi(proj_dir)` — —
- `extract_doql(proj_dir)` — Read app.doql.less (preferred) or app.doql.css as fallback.
- `extract_pyqual(proj_dir)` — —
- `extract_python_modules(proj_dir, pkg_name)` — —
- `extract_readme_title(proj_dir)` — —
- `extract_requirements(proj_dir)` — Parse requirements*.txt files — return list of {file, deps[]}.
- `extract_makefile(proj_dir)` — Parse Makefile — return list of {target, comment}.
- `extract_goal(proj_dir)` — Parse goal.yaml — versioning strategy, git conventions, build strategies.
- `extract_env(proj_dir)` — Parse .env.example — return list of {key, default, comment}.
- `extract_dockerfile(proj_dir)` — Parse Dockerfile — base image, exposed ports, entrypoint, labels.
- `extract_docker_compose(proj_dir)` — Parse docker-compose*.yml — services with images, ports, environment.
- `extract_package_json(proj_dir)` — Parse package.json — name, version, scripts, dependencies.
- `generate_map_toon(proj_dir)` — Generate project/map.toon.yaml content for proj_dir.
- `required_tools_for_profile(profile)` — Return the set of external tools needed to refresh analysis files for *profile*.
- `extract_source_snippets(proj_dir, pkg_name)` — Return per-module AST summary for source_snippets section.
- `extract_project_analysis(proj_dir, refactor)` — Return list of {file, lang, content} for files present in project/ subdir.
- `parse(content)` — Parse a SUMD markdown document.
- `parse_file(path)` — Parse a SUMD file.
- `validate(document)` — Validate a SUMD document.
- `validate_codeblocks(content, source)` — Validate all fenced code blocks in *content*.
- `validate_markdown(content, source, profile)` — Validate SUMD markdown structure.
- `validate_sumd_file(path, profile)` — Run all validators on a SUMD.md file.
- `generate_sumd_content(proj_dir, return_sources, raw_sources, profile)` — Generate SUMD.md content from a project directory.
- `list_tools()` — —
- `call_tool(name, arguments)` — —
- `main()` — —
- `cli()` — —
- `validate()` — —
- `export()` — —
- `info()` — —
- `generate()` — —
- `extract()` — —
- `scan()` — —
- `lint()` — —
- `analyze()` — —
- `scaffold()` — —
- `map_cmd()` — —
- `main()` — —
- `main_sumr()` — —
- `extract_pyproject()` — —
- `extract_taskfile()` — —
- `extract_openapi()` — —
- `extract_doql()` — —
- `extract_pyqual()` — —
- `extract_python_modules()` — —
- `extract_readme_title()` — —
- `extract_requirements()` — —
- `extract_makefile()` — —
- `extract_goal()` — —
- `extract_env()` — —
- `extract_dockerfile()` — —
- `extract_docker_compose()` — —
- `extract_package_json()` — —
- `generate_map_toon()` — —
- `required_tools_for_profile()` — —
- `extract_source_snippets()` — —
- `extract_project_analysis()` — —
- `run()` — —
- `generate_sumd_content()` — —
- `extract_testql_scenarios()` — —
- `parse()` — —
- `parse_file()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
- `build_context()` — —
- `ask()` — —
- `list_tools()` — —
- `call_tool()` — —
- `sumd_file()` — —
- `project_copy()` — —
- `test_sumd_scans_itself()` — —
- `test_sumd_scans_all_profiles()` — —
- `test_sumr_generates_sumr_md()` — —
- `test_sumd_lint_passes_on_generated_output()` — —
- `test_sumd_version_flag()` — —
- `test_sumd_scan_produces_no_unhandled_exceptions()` — —
- `test_parse_basic()` — —
- `test_parse_sections()` — —
- `test_validate_valid_document()` — —
- `test_validate_missing_intent()` — —
- `test_parse_file()` — —
- `test_parser_class()` — —
- `test_markpact_semantic_kinds_valid()` — —
- `test_markpact_unknown_kind_error()` — —
- `test_markpact_missing_path_error()` — —
- `proj_dir()` — —
- `test_pipeline_run_returns_string()` — —
- `test_pipeline_output_has_h1()` — —
- `test_pipeline_output_has_metadata()` — —
- `test_pipeline_return_sources()` — —
- `test_pipeline_profile_minimal()` — —
- `test_pipeline_profile_refactor()` — —
- `test_pipeline_with_modules()` — —
- `test_pipeline_with_taskfile()` — —
- `test_pipeline_with_dependencies()` — —
- `test_pipeline_injects_toc()` — —
- `test_required_tools_rich()` — —
- `test_required_tools_refactor()` — —
- `test_required_tools_minimal()` — —
- `test_refresh_map_toon_writes_file()` — —
- `test_refresh_analysis_files_noop_without_tools()` — —
- `make_ctx()` — —
- `test_placeholder()` — —
- `test_import()` — —
- `test_mcp_tools_registered()` — —
- `test_mcp_main_no_crash()` — —
- `print()` — —
- `generate_readme()` — —


## Project Structure

📄 `.pre-commit-config`
📄 `CHANGELOG`
📄 `README` (1 functions)
📄 `SPEC`
📄 `SUMD` (336 functions, 5 classes)
📄 `SUMR` (143 functions, 5 classes)
📄 `TODO` (5 functions)
📄 `Taskfile`
📄 `Taskfile.guards`
📄 `docs.README` (1 functions)
📄 `docs.USAGE` (6 functions)
📄 `examples.README`
📄 `examples.SUMD`
📄 `examples.basic.README`
📄 `examples.basic.demo`
📄 `examples.basic.sample-project.README`
📄 `examples.basic.sample-project.SUMD`
📄 `examples.basic.sample-project.Taskfile`
📄 `examples.basic.sample-project.goal`
📄 `examples.basic.sample-project.openapi`
📄 `examples.basic.sample-project.project.map.toon`
📄 `examples.basic.sample-project.pyproject`
📄 `examples.basic.sample-project.sumd`
📄 `examples.integrations.Dockerfile`
📄 `examples.integrations.README`
📄 `examples.integrations.docker-compose`
📄 `examples.integrations.github-actions`
📄 `examples.integrations.makefile`
📄 `examples.integrations.pre-commit-config`
📄 `examples.integrations.taskfile`
📄 `examples.integrations.vscode-tasks`
📄 `examples.llm.README`
📄 `examples.llm.anthropic_example` (2 functions)
📄 `examples.llm.context_injection`
📄 `examples.llm.llm_cli_example`
📄 `examples.llm.ollama_example`
📄 `examples.llm.openai_example` (3 functions)
📄 `examples.mcp.README`
📄 `examples.mcp.claude_desktop_config`
📄 `examples.mcp.continue_config`
📄 `examples.mcp.cursor_mcp`
📄 `examples.mcp.mcp_client` (2 functions)
📄 `examples.sumd`
📄 `goal`
📄 `mcp`
📄 `project`
📄 `project.README`
📄 `project.analysis.toon`
📄 `project.calls`
📄 `project.calls.toon`
📄 `project.context`
📄 `project.duplication.toon`
📄 `project.evolution.toon`
📄 `project.map.toon` (1530 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `project.validation.toon`
📄 `pyproject`
📄 `pyqual`
📄 `scripts.bootstrap`
📦 `sumd`
📄 `sumd.cli` (35 functions)
📄 `sumd.extractor` (39 functions)
📄 `sumd.generator`
📄 `sumd.mcp_server` (12 functions)
📄 `sumd.parser` (24 functions, 5 classes)
📄 `sumd.pipeline` (10 functions, 1 classes)
📄 `sumd.renderer` (54 functions)
📦 `sumd.sections`
📄 `sumd.sections.api_stubs` (2 functions, 1 classes)
📄 `sumd.sections.architecture` (2 functions, 1 classes)
📄 `sumd.sections.base` (2 functions, 2 classes)
📄 `sumd.sections.call_graph` (2 functions, 1 classes)
📄 `sumd.sections.code_analysis` (2 functions, 1 classes)
📄 `sumd.sections.configuration` (2 functions, 1 classes)
📄 `sumd.sections.dependencies` (2 functions, 1 classes)
📄 `sumd.sections.deployment` (2 functions, 1 classes)
📄 `sumd.sections.environment` (2 functions, 1 classes)
📄 `sumd.sections.extras` (2 functions, 1 classes)
📄 `sumd.sections.interfaces` (2 functions, 1 classes)
📄 `sumd.sections.metadata` (2 functions, 1 classes)
📄 `sumd.sections.quality` (2 functions, 1 classes)
📄 `sumd.sections.refactor_analysis` (2 functions, 1 classes)
📄 `sumd.sections.source_snippets` (2 functions, 1 classes)
📄 `sumd.sections.workflows` (2 functions, 1 classes)
📄 `sumd.toon_parser` (8 functions)
📄 `testql-scenarios.generated-cli-tests.testql.toon`
📄 `testql-scenarios.generated-from-pytests.testql.toon`
📄 `testql-scenarios.generated.generated-cli-tests.testql.toon`
📄 `testql-scenarios.smoke-generic.testql.toon`

## Requirements

- Python >= >=3.10
- click >=8.0- pyyaml >=6.0- toml >=0.10.0- goal >=2.1.0- costs >=0.1.20- pfix >=0.1.60

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Open an issue or pull request to get started.
### Development Setup

```bash
# Clone the repository
git clone https://github.com/oqlos/statement
cd sumd

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `examples` | Usage examples and code samples | [View](./examples) |

<!-- code2docs:end -->