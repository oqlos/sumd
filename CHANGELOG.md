# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.25] - 2026-04-22

### Docs
- Update README.md

## [0.3.24] - 2026-04-22

### Docs
- Update README.md

## [0.3.23] - 2026-04-22

### Docs
- Update README.md

### Test
- Update tests/test_cli.py

### Other
- Update sumd/cli.py

## [0.3.22] - 2026-04-22

### Docs
- Update README.md

### Test
- Update tests/test_cli.py

### Other
- Update sumd/cli.py

## [0.3.21] - 2026-04-21

### Docs
- Update README.md
- Update docs/README.md
- Update docs/USAGE.md
- Update project/README.md
- Update project/context.md

### Other
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 8 more files

## [0.3.20] - 2026-04-21

### Docs
- Update README.md

### Other
- Update sumd/cli.py

## [0.3.19] - 2026-04-21

### Docs
- Update README.md

### Other
- Update sumd/cli.py

## [0.3.18] - 2026-04-20

### Docs
- Update README.md

## [0.3.17] - 2026-04-20

### Docs
- Update README.md

## [0.3.16] - 2026-04-20

### Docs
- Update README.md
- Update docs/USAGE.md

## [0.3.15] - 2026-04-20

### Docs
- Update README.md

### Other
- Update sumd/cli.py

## [0.3.14] - 2026-04-20

### Docs
- Update README.md

## [0.3.13] - 2026-04-20

### Docs
- Update README.md

### Other
- Update sumd/cli.py

## [0.3.12] - 2026-04-20

### Docs
- Update README.md

## [0.3.11] - 2026-04-20

### Docs
- Update README.md

## [0.3.10] - 2026-04-20

### Docs
- Update README.md

## [0.3.9] - 2026-04-20

### Docs
- Update README.md

## [0.3.8] - 2026-04-20

### Docs
- Update README.md
- Update examples/basic/sample-project/SUMD.md

### Other
- Update examples/basic/sample-project/sumd.json
- Update sumd/parser.py

## [0.3.7] - 2026-04-19

### Docs
- Update README.md

## [0.3.6] - 2026-04-19

### Docs
- Update README.md

### Other
- Update sumd/cli.py

## [0.3.5] - 2026-04-19

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/README.md
- Update docs/USAGE.md
- Update examples/README.md
- Update examples/basic/README.md
- Update examples/basic/sample-project/README.md
- Update examples/basic/sample-project/SUMD.md
- Update examples/integrations/README.md
- ... and 5 more files

### Test
- Update tests/test_cli.py
- Update tests/test_mcp_server.py

### Other
- Update Taskfile.yml
- Update examples/basic/demo.sh
- Update examples/basic/sample-project/Taskfile.yml
- Update examples/basic/sample-project/goal.yaml
- Update examples/basic/sample-project/openapi.yaml
- Update examples/basic/sample-project/project/map.toon.yaml
- Update examples/basic/sample-project/pyproject.toml
- Update examples/basic/sample-project/sumd.json
- Update examples/integrations/Dockerfile
- Update examples/integrations/docker-compose.yml
- ... and 23 more files

## [0.3.4] - 2026-04-19

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMR.md
- Update TODO.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml

### Other
- Update project/analysis.toon.yaml
- Update project/duplication.toon.yaml
- Update project/map.toon.yaml
- Update project/validation.toon.yaml
- Update sumd/sections/__init__.py
- Update sumd/sections/call_graph.py
- Update sumd/sections/quality.py
- Update sumd/sections/workflows.py

## [0.3.3] - 2026-04-19

### Added
- SUMR `refactor` profile: 9 analysis sections — `workflows`, `quality`, `call_graph`, `test_contracts`, `api`, `cli`, `architecture`, `data_flow`, `dependencies`
- `sumd/sections/__init__.py` — section registry for profile dispatch

### Docs
- Removed AI cost tracking badges from README
- README updated to reflect v0.3.3 refactor profile capabilities

## [0.3.2] - 2026-04-19

### Docs
- Update README.md

## [0.3.1] - 2026-04-19

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Other
- Update .pyqual/pipeline.db
- Update Taskfile.yml
- Update VERSION
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 9 more files

## [0.2.0-rc1] - 2026-04-19

### Added
- `sumr` CLI command: generates `SUMR.md` (pre-refactoring analysis report) via `sumd scan . --profile refactor`
- `refactor` section profile → produces `SUMR.md` with subtitle "AI-aware project refactorization"
- `task doctor` smoke-test: 5 health checks (pyqual, pytest, ruff, sumd binary × 2)
- `publish` stage in pyqual pipeline: `twine-publish` runs automatically when all gates pass
- 88 unit tests across `test_pipeline.py`, `test_sections.py` (30), `test_extractor.py` (37)
- `--cov-branch` added to pytest `addopts` for accurate branch+statement coverage reporting
- pyqual gates: `coverage_min: 35`, `vallm_pass_min: 60`

### Fixed
- Single `.venv`: removed dual-venv split (`.venv` vs `venv`), all tasks use `{{.VENV_PY}} = .venv/bin/python`
- Coverage metric aligned between pyqual (branch+statement) and pytest report
- pyqual command order in Taskfile: `pyqual -c pyqual.yaml run` → `python -m pyqual run`
- `sumd/cli.py`: replaced hardcoded `__version__ = "0.1.24"` with `from sumd import __version__`

### Changed
- `SUMR.md` header: "AI-aware project refactorization" (was generic documentation subtitle)
- `Taskfile.yml`: all commands use `{{.VENV_PY}}` variable; `publish` task uses `python -m twine upload dist/*`

## [0.1.25] - 2026-04-19 (pre-release internal)

### Added
- `sumd .` / `sumd <path>` shortcut: first non-command argument treated as `scan <path> --fix`
- SUMR.md header updated to reflect "refactorization" purpose instead of "documentation"
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

