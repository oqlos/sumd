# examples/llm/

How to use `SUMD.md` and `SUMR.md` as context for LLM conversations, API calls, and automation.

## Examples

| File | Description |
|------|-------------|
| `context_injection.md` | Prompt patterns for injecting SUMD.md as context |
| `openai_example.py` | OpenAI GPT-4o API with SUMD context |
| `anthropic_example.py` | Anthropic Claude API with SUMD context |
| `ollama_example.sh` | Local LLM via Ollama |
| `llm_cli_example.sh` | simon-willison/llm CLI tool patterns |

## Quick Patterns

### Paste SUMD.md manually (ChatGPT / Claude web)

```bash
sumd scan . --fix --profile rich
cat SUMD.md
# Copy output → paste into ChatGPT / Claude / Gemini
```

Prompt template:
```
<context>
[SUMD.md content]
</context>

Based on the project above:
- What are the most complex modules?
- What testql scenarios are missing?
- Suggest a refactoring priority list.
```

### llm CLI (simon-willison/llm)

```bash
pip install llm

# Inject SUMD.md as system context
llm -s "$(cat SUMD.md)" "List all API endpoints"

# Use SUMR.md for refactoring advice
sumr .
llm -s "$(cat SUMR.md)" "Propose a refactoring plan"
```

### Shell one-liners

```bash
# Generate and query in one step
sumd scan . --fix && llm -s "$(cat SUMD.md)" "What is the intent of this project?"

# Extract a specific section and ask a targeted question
sumd extract SUMD.md --section Architecture | llm "Describe the data flow"
```
