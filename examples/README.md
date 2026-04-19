# SUMD Examples

Practical examples demonstrating `sumd` and `sumr` commands, LLM integration, MCP server, and tool integrations.

## Structure

| Directory | What it demonstrates |
|-----------|---------------------|
| [`basic/`](basic/) | CLI commands — scan, lint, map, scaffold |
| [`llm/`](llm/) | Using SUMD as LLM context (OpenAI, Anthropic, Ollama, llm CLI) |
| [`mcp/`](mcp/) | MCP server integration for Claude Desktop, Cursor, Continue.dev |
| [`integrations/`](integrations/) | GitHub Actions, pre-commit, VS Code, Docker, Taskfile |

## Quick Start

```bash
pip install sumd

# Generate SUMD.md for a project
sumd scan ./my-project --fix --profile rich

# Generate SUMR.md for refactoring analysis
sumr ./my-project

# Run the basic demo
bash examples/basic/demo.sh
```
