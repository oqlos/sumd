<!-- code2docs:start --># sumd

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-1105-green)
> **1105** functions | **101** classes | **120** files | CC̄ = 3.8

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
├── swop
├── goal
├── test
├── Makefile
├── working_script
├── SUMD
    ├── pre-commit-config
    ├── guards
├── script
├── pyqual
├── pyproject
├── TODO
├── mcp
├── CHANGELOG
├── Taskfile
├── simple_script
├── project
├── SPEC
├── README
    ├── USAGE
    ├── TESTQL_AUTOLOOP_ONBOARDING
    ├── README
    ├── SUMR
    ├── SUMD
    ├── sumd
    ├── README
            ├── toon
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
    ├── validator
    ├── cli
    ├── generator
├── sumd/
    ├── extractor
    ├── parser
    ├── models
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
        ├── swop
        ├── extras
        ├── api_stubs
        ├── environment
        ├── configuration
            ├── render
        ├── utils/
            ├── should_render
        ├── aggregates
        ├── commands
        ├── events
        ├── sumd_aggregate
    ├── cqrs/
        ├── queries
        ├── schema
        ├── commands
    ├── dsl/
        ├── parser
        ├── shell
        ├── schema_commands
        ├── nlp
    ├── install_testql_autoloop
    ├── bootstrap
            ├── testql-autoloop
            ├── testql-model-smoke
        ├── toon
        ├── toon
            ├── toon
            ├── toon
    ├── prompt
        ├── toon
        ├── toon
    ├── context
        ├── toon
        ├── toon
    ├── README
    ├── calls
        ├── toon
        ├── engine
```

## API Overview

### Classes

- **`RenderPipeline`** — —
- **`CodeBlockIssue`** — —
- **`RenderPipeline`** — —
- **`CodeBlockIssue`** — —
- **`CodeBlockIssue`** — —
- **`SUMDParser`** — Parser for SUMD markdown documents.
- **`SectionType`** — SUMD section types.
- **`Section`** — Represents a SUMD section.
- **`SUMDDocument`** — Represents a parsed SUMD document.
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
- **`SwopSection`** — —
- **`ExtrasSection`** — —
- **`ApiStubsSection`** — —
- **`EnvironmentSection`** — —
- **`ConfigurationSection`** — —
- **`AggregateRoot`** — Base aggregate root for event sourcing.
- **`EntityState`** — Base entity state for aggregates.
- **`Entity`** — Base entity for domain objects.
- **`ValueObject`** — Base value object.
- **`Repository`** — Base repository for aggregates.
- **`EventSourcedRepository`** — Event-sourced repository implementation.
- **`Command`** — Base command class for CQRS pattern.
- **`CommandHandler`** — Base command handler interface.
- **`CommandBus`** — Command bus for dispatching commands to appropriate handlers.
- **`CreateSumdDocument`** — Command to create a new SUMD document.
- **`UpdateSumdDocument`** — Command to update an existing SUMD document.
- **`AddSumdSection`** — Command to add a section to a SUMD document.
- **`RemoveSumdSection`** — Command to remove a section from a SUMD document.
- **`ValidateSumdDocument`** — Command to validate a SUMD document.
- **`ScanProject`** — Command to scan a project and generate SUMD.
- **`GenerateMap`** — Command to generate project map.
- **`ExecuteDslCommand`** — Command to execute DSL command.
- **`SumdCommandHandler`** — Base handler for SUMD commands.
- **`Event`** — Base event class for event sourcing.
- **`EventStore`** — In-memory event store with optional file persistence.
- **`SumdDocumentCreated`** — Event fired when a SUMD document is created.
- **`SumdDocumentUpdated`** — Event fired when a SUMD document is updated.
- **`SumdSectionAdded`** — Event fired when a section is added to SUMD document.
- **`SumdSectionRemoved`** — Event fired when a section is removed from SUMD document.
- **`SumdDocumentValidated`** — Event fired when a SUMD document is validated.
- **`SumdCommandExecuted`** — Event fired when a SUMD command is executed.
- **`SumdSection`** — Represents a section in a SUMD document.
- **`SumdDocumentState`** — State of a SUMD document aggregate.
- **`SumdAggregate`** — SUMD document aggregate root.
- **`Query`** — Base query class for CQRS pattern.
- **`QueryHandler`** — Base query handler interface.
- **`QueryBus`** — Query bus for dispatching queries to appropriate handlers.
- **`GetSumdDocument`** — Query to get a SUMD document.
- **`ListSumdSections`** — Query to list sections in a SUMD document.
- **`GetSumdSection`** — Query to get a specific section from a SUMD document.
- **`GetProjectInfo`** — Query to get project information.
- **`GetEventHistory`** — Query to get event history for an aggregate.
- **`GetAllEvents`** — Query to get all events from the event store.
- **`SearchDocuments`** — Query to search SUMD documents.
- **`GetValidationResults`** — Query to get validation results for a document.
- **`ExecuteDslQuery`** — Query to execute DSL query.
- **`SumdQueryHandler`** — Handler for SUMD queries.
- **`DSLDataType`** — Supported data types in DSL.
- **`DSLCommandType`** — Supported command types in DSL.
- **`DSLActionType`** — Supported action types in DSL.
- **`DSLParameter`** — DSL parameter definition.
- **`DSLCommandSchema`** — DSL command schema definition.
- **`DSLProjectSchema`** — DSL project schema definition.
- **`DSLExpression`** — DSL expression model.
- **`DSLStatement`** — DSL statement model.
- **`DSLScript`** — DSL script model.
- **`NLPIntent`** — NLP intent model.
- **`NLPEntity`** — NLP entity model.
- **`NLPModel`** — NLP model configuration.
- **`DSLContext`** — DSL execution context model.
- **`DSLCommandResult`** — DSL command execution result.
- **`DSLCommand`** — DSL command definition.
- **`DSLCommandRegistry`** — Registry for DSL commands.
- **`DSLTokenType`** — Token types for DSL parsing.
- **`DSLToken`** — Token in DSL.
- **`DSLLexer`** — Lexer for tokenizing DSL expressions.
- **`DSLExpressionType`** — Types of DSL expressions.
- **`DSLExpression`** — Expression in DSL.
- **`DSLParser`** — Parser for DSL expressions.
- **`DSLShell`** — Interactive shell for SUMD DSL.
- **`DSLShellServer`** — Server for DSL shell operations (for MCP integration).
- **`SchemaCommandRegistry`** — Registry for schema-based DSL commands.
- **`SchemaBasedCommands`** — Implementation of schema-based DSL commands.
- **`NLPProcessor`** — Natural Language Processor for DSL commands.
- **`NLPIntegration`** — NLP integration for DSL engine.
- **`SimpleNLPModel`** — Simple NLP model implementation for basic functionality.
- **`DSLContext`** — Execution context for DSL expressions.
- **`DSLEngine`** — Engine for executing DSL expressions.

### Functions

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
- `extract_swop()` — —
- `extract_project_analysis()` — —
- `run()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
- `list_tools()` — —
- `call_tool()` — —
- `print()` — —
- `print()` — —
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
- `extract_swop()` — —
- `extract_project_analysis()` — —
- `list_tools()` — —
- `call_tool()` — —
- `parse()` — —
- `parse_file()` — —
- `generate_sumd_content()` — —
- `extract_testql_scenarios()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
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
- `print()` — —
- `write_file()` — —
- `test_sumd_scans_itself()` — —
- `test_sumd_scans_all_profiles()` — —
- `test_sumr_generates_sumr_md()` — —
- `test_mcp_tools_registered()` — —
- `test_mcp_main_no_crash()` — —
- `print()` — —
- `write_file()` — —
- `print()` — —
- `scan()` — —
- `validate()` — —
- `print()` — —
- `ask()` — —
- `main()` — —
- `build_context()` — —
- `run()` — —
- `ask()` — —
- `main()` — —
- `build_context()` — —
- `run()` — —
- `ask(sumd_path, question, model)` — —
- `main()` — —
- `build_context(sumd_path)` — Return a focused context string from SUMD.md.
- `ask(sumd_path, question, model)` — —
- `main()` — —
- `run(sumd_file, single_tool, tool_args)` — —
- `main()` — —
- `extract_testql_scenarios(proj_dir)` — Scan all *.testql.toon.yaml and testql-scenarios/*.yaml files in project.
- `validate_codeblocks(content, source)` — Validate all fenced code blocks in *content*.
- `validate_markdown(content, source, profile)` — Validate SUMD markdown structure.
- `validate_sumd_file(path, profile)` — Run all validators on a SUMD.md file.
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
- `dsl(directory, command, script, interactive)` — SUMD DSL Shell - Domain Specific Language for SUMD operations.
- `cqrs_command(directory, command_type, aggregate_id, data)` — Execute CQRS command on SUMD aggregate.
- `nlp_command(text, directory, execute, verbose)` — Process natural language text and convert to DSL commands.
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
- `extract_swop(proj_dir)` — Extract SWOP manifest files from .swop/manifests/<context>/ directory.
- `extract_project_analysis(proj_dir, refactor)` — Return list of {file, lang, content} for files present in project/ subdir.
- `parse(content)` — Parse a SUMD markdown document.
- `parse_file(path)` — Parse a SUMD file.
- `validate(document)` — Validate a SUMD document.
- `generate_sumd_content(proj_dir, return_sources, raw_sources, profile)` — Generate SUMD.md content from a project directory.
- `list_tools()` — —
- `call_tool(name, arguments)` — —
- `main()` — —
- `call_with_ctx(render_fn)` — Return a ``render`` method that calls *render_fn* with ctx attributes.
- `always(_self, _ctx)` — Always render the section.
- `has_attr(attr)` — Return a ``should_render`` that checks ``bool(ctx.<attr>)``.
- `create_builtin_registry()` — Create registry with built-in commands.
- `parse_dsl(text)` — Parse DSL text into expression.
- `main()` — Main entry point for DSL shell.
- `log()` — —
- `write_if_missing()` — —
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
- `extract_swop()` — —
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
- `dsl()` — —
- `cqrs_command()` — —
- `nlp_command()` — —
- `main()` — —
- `main_sumr()` — —
- `parse_dsl()` — —
- `run()` — —
- `extract_testql_scenarios()` — —
- `validate_codeblocks()` — —
- `validate_markdown()` — —
- `validate_sumd_file()` — —
- `parse()` — —
- `parse_file()` — —
- `create_builtin_registry()` — —
- `build_context()` — —
- `ask()` — —
- `list_tools()` — —
- `call_tool()` — —
- `generate_sumd_content()` — —
- `call_with_ctx()` — —
- `always()` — —
- `has_attr()` — —
- `test_sumd_scans_itself()` — —
- `test_sumd_scans_all_profiles()` — —
- `test_sumr_generates_sumr_md()` — —
- `test_mcp_tools_registered()` — —
- `test_mcp_main_no_crash()` — —
- `print()` — —
- `write_file()` — —
- `sumd_file()` — —
- `project_copy()` — —
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
- `log()` — —
- `write_if_missing()` — —


## Project Structure

📄 `.pre-commit-config`
📄 `.windsurf.workflows.testql-autoloop`
📄 `.windsurf.workflows.testql-model-smoke`
📄 `CHANGELOG`
📄 `Makefile`
📄 `README` (4 functions)
📄 `SPEC`
📄 `SUMD` (353 functions, 2 classes)
📄 `SUMR` (126 functions, 2 classes)
📄 `TODO` (5 functions)
📄 `Taskfile`
📄 `Taskfile.guards`
📄 `docs.README`
📄 `docs.TESTQL_AUTOLOOP_ONBOARDING`
📄 `docs.USAGE` (6 functions)
📄 `examples.README`
📄 `examples.SUMD` (7 functions)
📄 `examples.SUMR`
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
📄 `examples.project.map.toon` (7 functions)
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
📄 `project.map.toon` (1008 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `project.validation.toon`
📄 `pyproject`
📄 `pyqual`
📄 `script` (19 functions)
📄 `scripts.bootstrap`
📄 `scripts.install_testql_autoloop` (2 functions)
📄 `simple_script` (17 functions)
📦 `sumd`
📄 `sumd.cli` (47 functions)
📦 `sumd.cqrs`
📄 `sumd.cqrs.aggregates` (23 functions, 6 classes)
📄 `sumd.cqrs.commands` (8 functions, 12 classes)
📄 `sumd.cqrs.events` (8 functions, 8 classes)
📄 `sumd.cqrs.queries` (17 functions, 13 classes)
📄 `sumd.cqrs.sumd_aggregate` (18 functions, 3 classes)
📦 `sumd.dsl`
📄 `sumd.dsl.commands` (28 functions, 2 classes)
📄 `sumd.dsl.engine` (40 functions, 2 classes)
📄 `sumd.dsl.nlp` (21 functions, 3 classes)
📄 `sumd.dsl.parser` (29 functions, 6 classes)
📄 `sumd.dsl.schema` (14 classes)
📄 `sumd.dsl.schema_commands` (33 functions, 2 classes)
📄 `sumd.dsl.shell` (14 functions, 2 classes)
📄 `sumd.extractor` (43 functions)
📄 `sumd.generator`
📄 `sumd.mcp_server` (18 functions)
📄 `sumd.models` (3 classes)
📄 `sumd.parser` (9 functions, 1 classes)
📄 `sumd.pipeline` (16 functions, 1 classes)
📄 `sumd.renderer` (1 functions)
📦 `sumd.sections`
📄 `sumd.sections.api_stubs` (2 functions, 1 classes)
📄 `sumd.sections.architecture` (8 functions, 1 classes)
📄 `sumd.sections.base` (2 functions, 2 classes)
📄 `sumd.sections.call_graph` (7 functions, 1 classes)
📄 `sumd.sections.code_analysis` (3 functions, 1 classes)
📄 `sumd.sections.configuration` (1 functions, 1 classes)
📄 `sumd.sections.dependencies` (4 functions, 1 classes)
📄 `sumd.sections.deployment` (5 functions, 1 classes)
📄 `sumd.sections.environment` (4 functions, 1 classes)
📄 `sumd.sections.extras` (4 functions, 1 classes)
📄 `sumd.sections.interfaces` (8 functions, 1 classes)
📄 `sumd.sections.metadata` (1 functions, 1 classes)
📄 `sumd.sections.quality` (3 functions, 1 classes)
📄 `sumd.sections.refactor_analysis` (1 functions, 1 classes)
📄 `sumd.sections.source_snippets` (1 functions, 1 classes)
📄 `sumd.sections.swop` (2 functions, 1 classes)
📦 `sumd.sections.utils`
📄 `sumd.sections.utils.render` (1 functions)
📄 `sumd.sections.utils.should_render` (2 functions)
📄 `sumd.sections.workflows` (4 functions, 1 classes)
📄 `sumd.toon_parser` (8 functions)
📄 `sumd.validator` (15 functions, 1 classes)
📄 `swop`
📄 `test` (1 functions)
📄 `testql-scenarios.generated-cli-tests.testql.toon`
📄 `testql-scenarios.generated-from-pytests.testql.toon`
📄 `working_script` (12 functions)

## Requirements

- Python >= >=3.10
- click >=8.3.3- pyyaml >=6.0.3- toml >=0.10.2- goal >=2.1.190- costs >=0.1.50- pfix >=0.1.72

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