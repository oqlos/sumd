# SUMD

## AI Cost Tracking

![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.50-green) ![AI Model](https://img.shields.io/badge/AI%20Model-openrouter%2Fqwen%2Fqwen3-coder-next-lightgrey)

This project uses AI-generated code. Total cost: **$1.5000** with **10** AI commits.

Generated on 2026-04-18 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/models/openrouter/qwen/qwen3-coder-next)

---



SUMD is a semantic project descriptor format in Markdown that defines intent, structure, execution entry points, and mental model of a system for both humans and LLMs.

## What is SUMD?

SUMD (Structured Unified Markdown Descriptor) is a lightweight structured markdown format for AI-aware project descriptions. It serves as a single source of truth for project documentation, optimized for both human readability and LLM context injection.

### Purpose

- **Project descriptor**: Defines API, CLI, workflows, endpoints, and system architecture
- **AI-optimized**: Structured for LLM consumption and automation tools
- **Lightweight manifest**: Bridges the gap between README, spec, and configuration files
- **Context injection**: Provides structured context for AI agents and tools

### Use Cases

- Project documentation and specification
- Input for LLM context injection
- CI/CD workflow descriptions
- API and CLI mapping
- Structural project manifest

## Installation

```bash
pip install sumd
```

## Usage

### CLI Commands

```bash
# Scan a workspace — auto-generate SUMD.md for every project found
sumd scan .                     # skip projects that already have SUMD.md
sumd scan . --fix               # overwrite existing SUMD.md
sumd scan . --fix --no-raw      # convert sources to structured Markdown instead of raw code blocks

# Validate a SUMD document
sumd validate SUMD.md

# Display information about a SUMD document
sumd info SUMD.md

# Export SUMD to different formats
sumd export SUMD.md --format json --output sumd.json
sumd export SUMD.md --format yaml --output sumd.yaml
sumd export SUMD.md --format toml --output sumd.toml
sumd export SUMD.md --format markdown --output sumd.md

# Generate SUMD from structured format
sumd generate sumd.json --format json --output SUMD.md
sumd generate sumd.yaml --format yaml --output SUMD.md
sumd generate sumd.toml --format toml --output SUMD.md

# Extract specific section
sumd extract SUMD.md --section intent
```

### Python API

```python
from sumd import parse, parse_file, validate

# Parse SUMD from string
document = parse(content)

# Parse SUMD from file
document = parse_file("SUMD.md")

# Validate SUMD document
errors = validate(document)
if errors:
    print("Validation errors:", errors)
else:
    print("SUMD document is valid")
```

## Ecosystem Architecture

SUMD is part of a three-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│                     SUMD (opis)                              │
│              Structured Unified Markdown Descriptor          │
│         Project description, intent, architecture            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOQL (wykonanie)                          │
│              Declarative Object Query Language               │
│              Data manipulation and execution                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Taskfile (runtime)                          │
│              Task runner and workflow execution              │
│              Automation and orchestration                   │
└─────────────────────────────────────────────────────────────┘
```

- **SUMD → opis (description)**: Defines what the system is and how it should work
- **DOQL → wykonanie (execution)**: Provides the language to manipulate and execute operations
- **Taskfile → runtime**: Manages the actual execution of workflows and tasks

## License

Licensed under Apache-2.0.
