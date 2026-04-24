# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/oqlos/sumd
- **Primary Language**: python
- **Languages**: python: 32, shell: 5
- **Analysis Mode**: static
- **Total Functions**: 231
- **Total Classes**: 24
- **Modules**: 37
- **Entry Points**: 80

## Architecture by Module

### sumd.cli
- **Functions**: 44
- **File**: `cli.py`

### sumd.extractor
- **Functions**: 40
- **File**: `extractor.py`

### sumd.pipeline
- **Functions**: 16
- **Classes**: 1
- **File**: `pipeline.py`

### sumd.validator
- **Functions**: 15
- **Classes**: 1
- **File**: `validator.py`

### sumd.mcp_server
- **Functions**: 12
- **File**: `mcp_server.py`

### sumd.sections.architecture
- **Functions**: 10
- **Classes**: 1
- **File**: `architecture.py`

### sumd.parser
- **Functions**: 9
- **Classes**: 1
- **File**: `parser.py`

### sumd.sections.interfaces
- **Functions**: 9
- **Classes**: 1
- **File**: `interfaces.py`

### sumd.toon_parser
- **Functions**: 8
- **File**: `toon_parser.py`

### sumd.sections.call_graph
- **Functions**: 8
- **Classes**: 1
- **File**: `call_graph.py`

### sumd.sections.deployment
- **Functions**: 7
- **Classes**: 1
- **File**: `deployment.py`

### sumd.sections.quality
- **Functions**: 5
- **Classes**: 1
- **File**: `quality.py`

### sumd.sections.dependencies
- **Functions**: 5
- **Classes**: 1
- **File**: `dependencies.py`

### sumd.sections.workflows
- **Functions**: 5
- **Classes**: 1
- **File**: `workflows.py`

### sumd.sections.extras
- **Functions**: 5
- **Classes**: 1
- **File**: `extras.py`

### sumd.sections.environment
- **Functions**: 4
- **Classes**: 1
- **File**: `environment.py`

### examples.llm.openai_example
- **Functions**: 3
- **File**: `openai_example.py`

### sumd.sections.code_analysis
- **Functions**: 3
- **Classes**: 1
- **File**: `code_analysis.py`

### sumd.sections.source_snippets
- **Functions**: 3
- **Classes**: 1
- **File**: `source_snippets.py`

### sumd.sections.swop
- **Functions**: 3
- **Classes**: 1
- **File**: `swop.py`

## Key Entry Points

Main execution flows into the system:

### sumd.cli.scan
> Scan a workspace directory and generate SUMD.md for every project found.

Detects projects by the presence of a known marker file (pyproject.toml,
pac
- **Calls**: cli.command, click.argument, click.option, click.option, click.option, click.option, click.option, click.option

### sumd.cli.analyze
> Run analysis tools (code2llm, redup, vallm) on a project.

Installs tools to .sumd-tools/venv and generates analysis files in project/.

PROJECT: Path
- **Calls**: cli.command, click.argument, click.option, click.option, project.resolve, click.echo, click.echo, sumd.cli._setup_tools_venv

### sumd.cli.scaffold
> Generate testql scenario scaffolds from OpenAPI spec or SUMD.md.

Reads openapi.yaml (if present) and generates .testql.toon.yaml scenario files
for e
- **Calls**: cli.command, click.argument, click.option, click.option, click.option, project.resolve, None.resolve, out_dir.mkdir

### sumd.pipeline.RenderPipeline._collect
> Extract all project data and build RenderContext.
- **Calls**: sumd.extractor.extract_pyproject, sumd.extractor.extract_taskfile, sumd.toon_parser.extract_testql_scenarios, sumd.extractor.extract_openapi, sumd.extractor.extract_doql, sumd.extractor.extract_pyqual, sumd.extractor.extract_python_modules, sumd.extractor.extract_readme_title

### sumd.cli.generate
> Generate a SUMD document from structured format.

FILE: Path to the structured format file (json/yaml/toml)
- **Calls**: cli.command, click.argument, click.option, click.option, file.read_text, lines.append, data.get, lines.append

### sumd.cli.map_cmd
> Generate project/map.toon.yaml — static code map in toon format.

Analyses all source files in the project and produces a map.toon.yaml
with module in
- **Calls**: cli.command, click.argument, click.option, click.option, click.option, project.resolve, click.echo, sumd.extractor.generate_map_toon

### sumd.cli.lint
> Validate SUMD.md files — check markdown structure and codeblock formats.

Validates:
  - Markdown structure (H1, required H2 sections, metadata fields
- **Calls**: cli.command, click.argument, click.option, click.option, sumd.cli._lint_collect_paths, sys.exit, click.echo, sys.exit

### sumd.cli.export
> Export a SUMD document to structured format.

FILE: Path to the SUMD markdown file
- **Calls**: cli.command, click.argument, click.option, click.option, sumd.parser.SUMDParser.parse_file, click.Path, click.Choice, click.Path

### examples.llm.openai_example.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, Path, print, print

### examples.llm.anthropic_example.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, Path, print, print

### sumd.parser.SUMDParser._parse_header
> Parse the project header (H1).

Args:
    lines: List of document lines
- **Calls**: enumerate, line.startswith, None.strip, header_content.split, None.strip, line.startswith, len, None.strip

### sumd.pipeline.RenderPipeline._assemble
> Assemble all section lines into final markdown.
- **Calls**: a, a, a, self._build_registered_sections, a, a, a, a

### sumd.sections.metadata.MetadataSection.render
- **Calls**: a, a, a, a, a, ctx.openapi.get, a, a

### sumd.cli.validate
> Validate a SUMD document.

FILE: Path to the SUMD markdown file
- **Calls**: cli.command, click.argument, sumd.parser.SUMDParser.parse_file, SUMDParser, parser.validate, click.Path, click.echo, sys.exit

### sumd.cli.extract
> Extract content from a SUMD document.

FILE: Path to the SUMD markdown file
- **Calls**: cli.command, click.argument, click.option, sumd.parser.SUMDParser.parse_file, click.Path, click.echo, sys.exit, click.echo

### examples.mcp.mcp_client.main
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.parse_args, Path, asyncio.run, sumd_path.exists

### sumd.parser.SUMDParser._parse_sections
> Parse all sections in the document.

Args:
    lines: List of document lines
- **Calls**: line.startswith, None.strip, sections.append, None.lower, self.SECTION_MAPPING.get, Section, None.strip, sections.append

### sumd.mcp_server._tool_export_sumd
- **Calls**: sumd.mcp_server._resolve_path, arguments.get, arguments.get, sumd.parser.SUMDParser.parse_file, sumd.mcp_server._doc_to_dict, sumd.mcp_server._resolve_path, out.write_text, types.TextContent

### sumd.mcp_server._tool_generate_sumd
- **Calls**: arguments.get, data.get, data.get, None.join, section.get, sumd.mcp_server._resolve_path, out.write_text, types.TextContent

### sumd.sections.refactor_analysis.RefactorAnalysisSection.render
- **Calls**: a, a, a, a, None.replace, a, a, a

### sumd.cli.info
> Display information about a SUMD document.

FILE: Path to the SUMD markdown file
- **Calls**: cli.command, click.argument, sumd.parser.SUMDParser.parse_file, click.echo, click.echo, click.echo, click.Path, click.echo

### sumd.mcp_server.list_tools
- **Calls**: server.list_tools, types.Tool, types.Tool, types.Tool, types.Tool, types.Tool, types.Tool, types.Tool

### sumd.mcp_server._tool_get_section
- **Calls**: sumd.mcp_server._resolve_path, None.lower, sumd.parser.SUMDParser.parse_file, next, types.TextContent, types.TextContent, json.dumps, s.name.lower

### sumd.mcp_server._tool_validate_sumd
- **Calls**: sumd.mcp_server._resolve_path, sumd.parser.SUMDParser.parse_file, SUMDParser, parser.validate, json.dumps, types.TextContent, len

### sumd.validator._validate_deps_body
> Each line of a deps block should be a valid pip requirement or empty.
- **Calls**: enumerate, body.splitlines, line.strip, line.startswith, re.match, issues.append

### sumd.pipeline.RenderPipeline._build_registered_sections
> Run all registered Section classes that match the profile.
- **Calls**: PROFILES.get, set, cls, rendered.append, section.should_render, section.render

### sumd.validator._validate_mermaid_body
> Check mermaid block starts with a valid diagram type.
- **Calls**: None.strip, any, None.split, first.startswith, body.strip

### sumd.mcp_server._tool_parse_sumd
- **Calls**: sumd.mcp_server._resolve_path, sumd.parser.SUMDParser.parse_file, types.TextContent, json.dumps, sumd.mcp_server._doc_to_dict

### sumd.mcp_server._tool_info_sumd
- **Calls**: sumd.mcp_server._resolve_path, sumd.parser.SUMDParser.parse_file, len, types.TextContent, json.dumps

### sumd.mcp_server.call_tool
- **Calls**: server.call_tool, _TOOL_HANDLERS.get, handler, types.TextContent, types.TextContent

## Process Flows

Key execution flows identified:

### Flow 1: scan
```
scan [sumd.cli]
```

### Flow 2: analyze
```
analyze [sumd.cli]
```

### Flow 3: scaffold
```
scaffold [sumd.cli]
```

### Flow 4: _collect
```
_collect [sumd.pipeline.RenderPipeline]
  └─ →> extract_pyproject
      └─> _read_toml
  └─ →> extract_taskfile
  └─ →> extract_testql_scenarios
```

### Flow 5: generate
```
generate [sumd.cli]
```

### Flow 6: map_cmd
```
map_cmd [sumd.cli]
```

### Flow 7: lint
```
lint [sumd.cli]
  └─> _lint_collect_paths
```

### Flow 8: export
```
export [sumd.cli]
  └─ →> parse_file
```

### Flow 9: main
```
main [examples.llm.openai_example]
```

### Flow 10: _parse_header
```
_parse_header [sumd.parser.SUMDParser]
```

## Key Classes

### sumd.parser.SUMDParser
> Parser for SUMD markdown documents.
- **Methods**: 6
- **Key Methods**: sumd.parser.SUMDParser.__init__, sumd.parser.SUMDParser.parse, sumd.parser.SUMDParser.parse_file, sumd.parser.SUMDParser._parse_header, sumd.parser.SUMDParser._parse_sections, sumd.parser.SUMDParser.validate

### sumd.pipeline.RenderPipeline
> Collect project data → build sections → render → inject TOC.

Usage:
    pipeline = RenderPipeline(p
- **Methods**: 6
- **Key Methods**: sumd.pipeline.RenderPipeline.__init__, sumd.pipeline.RenderPipeline._collect, sumd.pipeline.RenderPipeline._build_registered_sections, sumd.pipeline.RenderPipeline._render_legacy_sections, sumd.pipeline.RenderPipeline._assemble, sumd.pipeline.RenderPipeline.run

### sumd.sections.interfaces.InterfacesSection
- **Methods**: 2
- **Key Methods**: sumd.sections.interfaces.InterfacesSection.should_render, sumd.sections.interfaces.InterfacesSection.render

### sumd.sections.refactor_analysis.RefactorAnalysisSection
- **Methods**: 2
- **Key Methods**: sumd.sections.refactor_analysis.RefactorAnalysisSection.should_render, sumd.sections.refactor_analysis.RefactorAnalysisSection.render

### sumd.sections.quality.QualitySection
- **Methods**: 2
- **Key Methods**: sumd.sections.quality.QualitySection.should_render, sumd.sections.quality.QualitySection.render

### sumd.sections.deployment.DeploymentSection
- **Methods**: 2
- **Key Methods**: sumd.sections.deployment.DeploymentSection.should_render, sumd.sections.deployment.DeploymentSection.render

### sumd.sections.code_analysis.CodeAnalysisSection
- **Methods**: 2
- **Key Methods**: sumd.sections.code_analysis.CodeAnalysisSection.should_render, sumd.sections.code_analysis.CodeAnalysisSection.render

### sumd.sections.metadata.MetadataSection
> Render ## Metadata — always present, all profiles.
- **Methods**: 2
- **Key Methods**: sumd.sections.metadata.MetadataSection.should_render, sumd.sections.metadata.MetadataSection.render

### sumd.sections.dependencies.DependenciesSection
- **Methods**: 2
- **Key Methods**: sumd.sections.dependencies.DependenciesSection.should_render, sumd.sections.dependencies.DependenciesSection.render

### sumd.sections.call_graph.CallGraphSection
- **Methods**: 2
- **Key Methods**: sumd.sections.call_graph.CallGraphSection.should_render, sumd.sections.call_graph.CallGraphSection.render

### sumd.sections.architecture.ArchitectureSection
- **Methods**: 2
- **Key Methods**: sumd.sections.architecture.ArchitectureSection.should_render, sumd.sections.architecture.ArchitectureSection.render

### sumd.sections.source_snippets.SourceSnippetsSection
- **Methods**: 2
- **Key Methods**: sumd.sections.source_snippets.SourceSnippetsSection.should_render, sumd.sections.source_snippets.SourceSnippetsSection.render

### sumd.sections.swop.SwopSection
- **Methods**: 2
- **Key Methods**: sumd.sections.swop.SwopSection.should_render, sumd.sections.swop.SwopSection.render

### sumd.sections.workflows.WorkflowsSection
- **Methods**: 2
- **Key Methods**: sumd.sections.workflows.WorkflowsSection.should_render, sumd.sections.workflows.WorkflowsSection.render

### sumd.sections.extras.ExtrasSection
- **Methods**: 2
- **Key Methods**: sumd.sections.extras.ExtrasSection.should_render, sumd.sections.extras.ExtrasSection.render

### sumd.sections.api_stubs.ApiStubsSection
- **Methods**: 2
- **Key Methods**: sumd.sections.api_stubs.ApiStubsSection.should_render, sumd.sections.api_stubs.ApiStubsSection.render

### sumd.sections.configuration.ConfigurationSection
- **Methods**: 2
- **Key Methods**: sumd.sections.configuration.ConfigurationSection.should_render, sumd.sections.configuration.ConfigurationSection.render

### sumd.sections.environment.EnvironmentSection
- **Methods**: 2
- **Key Methods**: sumd.sections.environment.EnvironmentSection.should_render, sumd.sections.environment.EnvironmentSection.render

### sumd.sections.base.Section
> Protocol for all SUMD section renderers.

Attributes:
    name:     unique identifier used in PROFIL
- **Methods**: 2
- **Key Methods**: sumd.sections.base.Section.should_render, sumd.sections.base.Section.render
- **Inherits**: Protocol

### sumd.validator.CodeBlockIssue
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### sumd.toon_parser._parse_toon_block_config
> Extract CONFIG key-value pairs from toon file lines.
- **Output to**: re.match, re.match, line.startswith, re.match, m.group

### sumd.toon_parser._parse_toon_block_api
> Extract API endpoint rows from toon content.
- **Output to**: re.findall, None.strip, endpoints.append, int

### sumd.toon_parser._parse_toon_block_assert
> Extract ASSERT rows from toon file lines.
- **Output to**: re.match, re.match, line.startswith, re.match, rows.append

### sumd.toon_parser._parse_toon_block_performance
> Extract PERFORMANCE rows from toon file lines.
- **Output to**: re.match, re.match, line.startswith, re.match, rows.append

### sumd.toon_parser._parse_toon_block_navigate
> Extract NAVIGATE url rows from toon file lines.
- **Output to**: re.match, re.match, line.startswith, line.strip, urls.append

### sumd.toon_parser._parse_toon_block_gui
> Extract GUI action rows from toon file lines.
- **Output to**: re.match, re.match, line.startswith, re.match, actions.append

### sumd.toon_parser._parse_toon_file
> Parse a single *.testql.toon.yaml file into a scenario dict.
- **Output to**: f.read_text, content.splitlines, re.search, str, _match

### sumd.parser.SUMDParser.parse
> Parse a SUMD markdown document.

Args:
    content: The markdown content to parse

Returns:
    SUMD
- **Output to**: SUMDDocument, content.split, self._parse_header, self._parse_sections

### sumd.parser.SUMDParser.parse_file
> Parse a SUMD file.

Args:
    path: Path to the SUMD markdown file

Returns:
    SUMDDocument: Parse
- **Output to**: path.read_text, self.parse

### sumd.parser.SUMDParser._parse_header
> Parse the project header (H1).

Args:
    lines: List of document lines
- **Output to**: enumerate, line.startswith, None.strip, header_content.split, None.strip

### sumd.parser.SUMDParser._parse_sections
> Parse all sections in the document.

Args:
    lines: List of document lines
- **Output to**: line.startswith, None.strip, sections.append, None.lower, self.SECTION_MAPPING.get

### sumd.parser.SUMDParser.validate
> Validate a SUMD document against the specification.

Args:
    document: The document to validate

R
- **Output to**: errors.append, errors.append, errors.append, errors.append

### sumd.parser.parse
> Parse a SUMD markdown document.

Args:
    content: The markdown content to parse

Returns:
    SUMD
- **Output to**: SUMDParser, parser.parse

### sumd.parser.parse_file
> Parse a SUMD file.

Args:
    path: Path to the SUMD markdown file

Returns:
    SUMDDocument: Parse
- **Output to**: SUMDParser, parser.parse_file

### sumd.parser.validate
> Validate a SUMD document.

Args:
    document: The document to validate

Returns:
    List of valida
- **Output to**: SUMDParser, parser.validate

### sumd.validator._validate_yaml_body
> Check YAML body is parseable.
- **Output to**: yaml.safe_load

### sumd.validator._validate_less_css_body
> Basic sanity: balanced braces.
- **Output to**: body.count, body.count

### sumd.validator._validate_mermaid_body
> Check mermaid block starts with a valid diagram type.
- **Output to**: None.strip, any, None.split, first.startswith, body.strip

### sumd.validator._validate_toon_body
> Check toon block has at least one recognised section header.
- **Output to**: re.findall

### sumd.validator._validate_bash_body
> Check bash block is non-empty and doesn't contain obvious placeholders.
- **Output to**: body.strip

### sumd.validator._validate_deps_body
> Each line of a deps block should be a valid pip requirement or empty.
- **Output to**: enumerate, body.splitlines, line.strip, line.startswith, re.match

### sumd.validator._validate_markpact_meta
> Check markpact annotation kind and required attributes.
- **Output to**: mp.group, _MARKPACT_REQUIRED_ATTRS.get, mp.group, issues.append, issues.append

### sumd.validator.validate_codeblocks
> Validate all fenced code blocks in *content*.

Checks:
- markpact annotation syntax (kind, required 
- **Output to**: _CODEBLOCK_RE.finditer, None.strip, None.strip, None.strip, _MARKPACT_META_RE.search

### sumd.validator.validate_markdown
> Validate SUMD markdown structure.

Checks:
- H1 title present
- Required H2 sections present (profil
- **Output to**: content.splitlines, sumd.validator._check_empty_links, sumd.validator._check_unclosed_fences, sumd.validator._check_metadata_fields, sumd.validator._check_h1

### sumd.validator.validate_sumd_file
> Run all validators on a SUMD.md file.

Returns:
    {
      "source": str,
      "markdown": list[st
- **Output to**: path.read_text, sumd.validator.validate_markdown, sumd.validator.validate_codeblocks, str, any

## Behavioral Patterns

### recursion__walk_projects
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: sumd.cli._walk_projects

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `examples.mcp.mcp_client.run` - 53 calls
- `sumd.cli.scan` - 38 calls
- `sumd.cli.analyze` - 33 calls
- `sumd.cli.scaffold` - 33 calls
- `sumd.cli.generate` - 30 calls
- `sumd.extractor.extract_goal` - 24 calls
- `sumd.extractor.generate_map_toon` - 24 calls
- `sumd.extractor.extract_docker_compose` - 22 calls
- `sumd.cli.map_cmd` - 20 calls
- `sumd.cli.lint` - 19 calls
- `sumd.validator.validate_codeblocks` - 17 calls
- `sumd.extractor.extract_pyproject` - 17 calls
- `sumd.cli.export` - 16 calls
- `examples.llm.openai_example.main` - 15 calls
- `sumd.extractor.extract_package_json` - 15 calls
- `examples.llm.anthropic_example.main` - 14 calls
- `sumd.sections.metadata.MetadataSection.render` - 14 calls
- `sumd.extractor.extract_openapi` - 13 calls
- `sumd.extractor.extract_env` - 13 calls
- `sumd.cli.validate` - 13 calls
- `sumd.cli.extract` - 13 calls
- `examples.mcp.mcp_client.main` - 12 calls
- `sumd.toon_parser.extract_testql_scenarios` - 12 calls
- `sumd.extractor.extract_pyqual` - 12 calls
- `sumd.extractor.extract_makefile` - 12 calls
- `sumd.extractor.extract_source_snippets` - 12 calls
- `sumd.sections.refactor_analysis.RefactorAnalysisSection.render` - 11 calls
- `sumd.cli.info` - 11 calls
- `sumd.extractor.extract_taskfile` - 10 calls
- `examples.llm.openai_example.build_context` - 9 calls
- `sumd.extractor.extract_requirements` - 9 calls
- `sumd.extractor.extract_swop` - 9 calls
- `sumd.mcp_server.list_tools` - 8 calls
- `sumd.extractor.extract_project_analysis` - 7 calls
- `sumd.validator.validate_markdown` - 6 calls
- `sumd.validator.validate_sumd_file` - 5 calls
- `sumd.extractor.extract_readme_title` - 5 calls
- `sumd.extractor.extract_dockerfile` - 5 calls
- `sumd.mcp_server.call_tool` - 5 calls
- `sumd.parser.SUMDParser.parse` - 4 calls

## System Interactions

How components interact:

```mermaid
graph TD
    scan --> command
    scan --> argument
    scan --> option
    analyze --> command
    analyze --> argument
    analyze --> option
    analyze --> resolve
    scaffold --> command
    scaffold --> argument
    scaffold --> option
    _collect --> extract_pyproject
    _collect --> extract_taskfile
    _collect --> extract_testql_scena
    _collect --> extract_openapi
    _collect --> extract_doql
    generate --> command
    generate --> argument
    generate --> option
    generate --> read_text
    map_cmd --> command
    map_cmd --> argument
    map_cmd --> option
    lint --> command
    lint --> argument
    lint --> option
    lint --> _lint_collect_paths
    export --> command
    export --> argument
    export --> option
    export --> parse_file
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.