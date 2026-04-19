# SUMD Documentation

> **Version 0.3.4** | [Project README](../README.md) | [Usage Guide](USAGE.md) | [Specification](../SPEC.md)

## Overview

SUMD (Structured Unified Markdown Descriptor) is a semantic project descriptor format —
a machine-readable, LLM-optimised Markdown file that captures a project's intent,
architecture, interfaces, workflows, and quality contracts in a single document.

## Contents

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview, installation, quick start |
| [USAGE.md](USAGE.md) | Full CLI and API usage guide |
| [SPEC.md](../SPEC.md) | SUMD format specification |
| [CHANGELOG.md](../CHANGELOG.md) | Version history |
| [examples/](../examples/) | Practical examples |

## Quick Reference

### Generate SUMD.md for your project

```bash
pip install sumd
sumd scan . --fix --profile rich   # generates SUMD.md
```

### Generate SUMR.md (pre-refactoring analysis)

```bash
sumr .    # generates SUMR.md with code complexity, duplication, call graph
```

### Validate

```bash
sumd lint SUMD.md
sumd lint --workspace . --json
```

### Use with LLMs

```bash
# Inject into any LLM chat as context
cat SUMD.md

# Use with llm CLI
llm -s "$(cat SUMD.md)" "What should I refactor first?"

# Use MCP server with Claude Desktop, Cursor, Windsurf, Continue.dev
python -m sumd.mcp_server
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `sumd .` | Smart scan — generate/update SUMD.md |
| `sumd scan . --fix` | Generate SUMD.md for all projects in workspace |
| `sumr .` | Generate SUMR.md (refactor analysis profile) |
| `sumd lint SUMD.md` | Validate SUMD.md structure |
| `sumd map .` | Generate static code map (`project/map.toon.yaml`) |
| `sumd scaffold .` | Generate testql scenario skeletons |
| `sumd analyze .` | Run code2llm / redup / vallm analysis |
| `sumd validate SUMD.md` | Parse + validate (exit 1 on errors) |
| `sumd export SUMD.md` | Export to JSON / YAML / TOML |
| `sumd info SUMD.md` | Show project name, description, sections |

## Section Profiles

| Profile | Use case |
|---------|---------|
| `minimal` | Minimal sections — CI, badges |
| `light` | Standard documentation |
| `rich` | Full content — LLM context injection (default) |
| `refactor` | Pre-refactoring analysis → `SUMR.md` |

## MCP Tools

SUMD exposes 7 MCP tools for LLM agent integration:

`parse_sumd` · `validate_sumd` · `export_sumd` · `list_sections` · `get_section` · `info_sumd` · `generate_sumd`

See [USAGE.md — MCP Server](USAGE.md#mcp-server) for configuration examples (Claude Desktop, Cursor, Continue.dev).

## Examples

Practical examples are in [`examples/`](../examples/):

| Directory | What it demonstrates |
|-----------|---------------------|
| `examples/basic/` | CLI commands: scan, lint, map, scaffold |
| `examples/llm/` | LLM context injection patterns |
| `examples/mcp/` | MCP server integration |
| `examples/integrations/` | GitHub Actions, pre-commit, VS Code, Docker |
