# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Metadata

- **name**: `sumd`
- **version**: `0.1.10`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### Source Modules

- `sumd.cli`
- `sumd.mcp_server`
- `sumd.parser`

## Interfaces

### CLI Entry Points

- `sumd`
- `sumd-mcp`

## Workflows

## Configuration

```yaml
project:
  name: sumd
  version: 0.1.10
  env: local
```

## Dependencies

### Runtime

- `click>=8.0`
- `pyyaml>=6.0`
- `toml>=0.10.0`

## Deployment

```bash
pip install sumd

# development install
pip install -e .[dev]
```
