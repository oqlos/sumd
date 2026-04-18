# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `sumd .` / `sumd <path>` shortcut: first non-command argument treated as `scan <path> --fix`
- Recursive project discovery: `_detect_projects` now walks subdirectories at any depth (skips `.venv`, `node_modules`, `.git`, `build`, `dist`, `.sumd-tools`, etc.)
- `--depth N` flag for `scan`: limit recursive search depth (default: unlimited)
- Auto-detect workspace-as-project: if workspace root has `pyproject.toml` and no subdirectory projects are found, scans root as single project
- Section profiles: `--profile minimal/light/rich` (default: `rich`) — 15 sections across 3 tiers
- 5 new rich-profile sections: `SourceSnippets`, `ApiStubs`, `TestContracts`, `CallGraph`, `EnvironmentSection`
- Semantic markpact kinds: `markpact:doql`, `markpact:openapi`, `markpact:testql`, `markpact:taskfile`, `markpact:pyqual`, `markpact:analysis` (replacing generic `markpact:file`)
- Node.js project support: `DependenciesSection` now renders `package.json` deps (`markpact:deps node`)
- `CallGraphSection`: HUBS table (top-8 by degree) with ⚠ flags for high-Fan-In hubs
- `ApiStubsSection`: OpenAPI endpoints as Python-like stubs grouped by tag
- `TestContractsSection`: testql scenarios as contract signatures grouped by type
- `SourceSnippetsSection`: top-5 modules sorted by complexity with CC/fan annotations

### Changed
- `generate_sumd_content` refactored to 4-line shim delegating to `RenderPipeline` (fan-out: 34→2)
- `_render_code_analysis` accepts `skip_files` param to avoid duplicating call graph data
- Parser `_VALID_MARKPACT_KINDS` whitelist extended with 6 new semantic kinds

## [0.1.24] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update sumd.json
- Update sumd/cli.py

## [0.1.23] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.toon.yaml
- Update project/compact_flow.mmd
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/index.html
- Update project/validation.toon.yaml
- Update sumd.json
- ... and 8 more files

## [0.1.22] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Test
- Update tests/test_parser.py

### Other
- Update sumd.json
- Update sumd/parser.py
- Update sumd/renderer.py
- Update sumd/sections/__init__.py
- Update sumd/sections/api_stubs.py
- Update sumd/sections/dependencies.py
- Update sumd/sections/test_contracts.py

## [0.1.21] - 2026-04-18

### Docs
- Update README.md

## [0.1.20] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update sumd.json
- Update sumd/extractor.py
- Update sumd/pipeline.py
- Update sumd/renderer.py
- Update sumd/sections/__init__.py
- Update sumd/sections/base.py
- Update sumd/sections/source_snippets.py

## [0.1.19] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update project/map.toon.yaml
- Update sumd.json
- Update sumd/cli.py
- Update sumd/pipeline.py
- Update sumd/sections/__init__.py
- Update sumd/sections/architecture.py
- Update sumd/sections/base.py
- Update sumd/sections/code_analysis.py
- Update sumd/sections/configuration.py
- Update sumd/sections/dependencies.py
- ... and 7 more files

## [0.1.18] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md
- Update project/context.md

### Other
- Update project/calls.mmd
- Update project/calls.toon.yaml
- Update project/compact_flow.mmd
- Update project/flow.mmd
- Update sumd.json

## [0.1.17] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.toon.yaml
- Update project/compact_flow.mmd
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- Update project/index.html
- Update project/validation.toon.yaml
- Update sumd.json
- ... and 4 more files

## [0.1.16] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md
- Update TODO.md
- Update code2llm_output/README.md
- Update code2llm_output/context.md
- Update docs/README.md
- Update docs/USAGE.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/smoke-generic.testql.toon.yaml

### Other
- Update app.doql.less
- Update code2llm_output/index.html
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 14 more files

## [0.1.15] - 2026-04-18

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update docs/USAGE.md

### Other
- Update sumd.json
- Update sumd/cli.py
- Update sumd/generator.py

## [0.1.15] - 2026-04-18

### Added
- `sumd scan` command: auto-generates `SUMD.md` for every project in a workspace
- `--raw/--no-raw` flag for `scan` (default: `--raw`): embed source files as fenced code blocks or convert to structured Markdown
- Raw rendering for `app.doql.less/css`, `openapi.yaml`, `pyqual.yaml`, and testql scenario files

### Fixed
- Empty workflow steps caused by `{{.PWD}}`-style template vars in Taskfile (`_BLOCK` regex updated)
- Quoted trigger values (`"manual"`) now unquoted in DOQL workflow parsing
- Duplicate workflows when both `.less` and `.css` files are present (deduplication via `workflows_map`)
- Inline comments in `.env.example` values now correctly stripped

### Docs
- Updated README.md with `scan` command examples
- Updated docs/USAGE.md with `scan` section and `--raw/--no-raw` usage table

## [0.1.14] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update sumd.json
- Update sumd/generator.py

## [0.1.13] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update sumd.json
- Update sumd/generator.py

## [0.1.12] - 2026-04-18

### Docs
- Update README.md
- Update SUMD.md

### Other
- Update Taskfile.yml
- Update app.doql.css
- Update app.doql.less
- Update scripts/generate_all_sumd.py
- Update sumd.json
- Update sumd/__init__.py
- Update sumd/generator.py

## [0.1.11] - 2026-04-18

### Docs
- Update README.md

### Other
- Update scripts/generate_all_sumd.py
- Update sumd/cli.py

## [0.1.10] - 2026-04-18

### Docs
- Update README.md
- Update SPEC.md
- Update SUMD.md

### Other
- Update scripts/generate_all_sumd.py
- Update sumd.json

## [0.1.9] - 2026-04-18

### Docs
- Update README.md
- Update SPEC.md
- Update docs/USAGE.md
- Update examples/SUMD.md

### Other
- Update examples/sumd.json
- Update mcp.json
- Update sumd/mcp_server.py

## [0.1.8] - 2026-04-18

### Docs
- Update README.md

## [0.1.7] - 2026-04-18

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD-SPEC.md

### Test
- Update tests/test_parser.py

### Other
- Update VERSION
- Update sumd/__init__.py
- Update sumd/cli.py
- Update sumd/parser.py

## [0.1.6] - 2026-04-18

### Added
- Multi-format export support (markdown, json, yaml, toml)
- Generate command to create SUMD from structured formats
- CLI `--output` option for export and generate commands
- Format conversion schema documentation in SUMD-SPEC.md

### Changed
- Updated README with installation and usage examples
- Updated SUMD-SPEC.md with format conversion section
- Added toml dependency to pyproject.toml

### Fixed
- Added Optional import to cli.py

## [0.1.5] - 2026-04-18

### Added
- SUMD v1 specification document
- Python parser for SUMD format
- CLI tool with validate, export, info, extract commands
- Ecosystem architecture documentation (SUMD/DOQL/Taskfile)

### Changed
- Renamed package from statement to sumd
- Updated package description and keywords

## [0.1.4] - 2026-04-18

## [0.1.3] - 2026-04-18

### Test
- Update tests/test_statement.py

### Other
- Update sumd/__init__.py

## [0.1.2] - 2026-04-18

### Test
- Update tests/test_statement.py

### Other
- Update overview/__init__.py

## [0.1.1] - 2026-04-18

### Docs
- Update README.md

### Test
- Update tests/test_statement.py

### Other
- Update .env.example
- Update VERSION
- Update statement/__init__.py

## [0.0.1] - 2026-04-18

