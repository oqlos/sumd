# LLM Context Injection with SUMD

This guide explains how to use `SUMD.md` and `SUMR.md` as structured context
for LLM conversations and API calls.

## Why SUMD.md?

A well-formed `SUMD.md` file contains:
- Project intent (the "why")
- Architecture overview
- All API endpoints and CLI commands
- Existing test contracts
- Quality metrics and hotspots
- Environment variables

This gives an LLM **complete project understanding in a single file** — no need to share source code.

## Patterns

### Pattern 1: Manual Chat (ChatGPT / Claude web)

```bash
sumd scan . --fix --profile rich
cat SUMD.md
```

1. Copy the output
2. Paste into ChatGPT, Claude, or Gemini chat
3. Ask your question

**Effective prompt templates:**

```
<context>
[SUMD.md content]
</context>

Based on the project above:
- What are the most complex modules? (look at Call Graph)
- What testql scenarios are missing?
- Generate a new testql scenario for the POST /items endpoint.
```

---

### Pattern 2: llm CLI

```bash
pip install llm
llm keys set openai

# Single question
llm -s "$(cat SUMD.md)" "List all API endpoints with their HTTP methods."

# Refactoring advice using SUMR.md
sumr .
llm -s "$(cat SUMR.md)" "Propose a refactoring plan — focus on hotspots and duplication."

# Pipe a section directly
sumd extract SUMD.md --section Architecture | llm "Describe the data flow in plain English."
```

---

### Pattern 3: OpenAI API

```python
# See openai_example.py for full code
from sumd import parse_file
import openai

doc = parse_file("SUMD.md")
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": f"Project context:\n{doc.raw_content}"},
        {"role": "user",   "content": "What is the main entry point?"},
    ],
)
```

---

### Pattern 4: Anthropic Claude API

```python
# See anthropic_example.py for full code
from sumd import parse_file
import anthropic

doc = parse_file("SUMD.md")
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system=f"You are an expert on {doc.project_name}.\n\n{doc.raw_content}",
    messages=[{"role": "user", "content": "What tests should I add?"}],
)
```

---

### Pattern 5: Local LLM via Ollama

```bash
# See ollama_example.sh for the shell version
ollama pull llama3
ollama run llama3 "$(printf 'Context:\n%s\n\nQuestion: Summarise this project.' "$(cat SUMD.md)")"
```

---

### Pattern 6: Targeted section injection

Instead of the full SUMD.md, inject only the sections relevant to your question:

```python
from sumd import parse_file

doc = parse_file("SUMD.md")

# Get only the sections needed for a test-generation task
relevant = {s.name.lower(): s.content for s in doc.sections}
test_context = "\n\n".join([
    relevant.get("interfaces", ""),
    relevant.get("test contracts", ""),
    relevant.get("api stubs", ""),
])

prompt = f"Given these API contracts:\n\n{test_context}\n\nGenerate a testql scenario for the DELETE endpoint."
```

---

## Token Budget Tips

| Profile | Approx. tokens | Use case |
|---------|---------------|---------|
| `minimal` | ~500 | Quick overview, CI |
| `light` | ~1 500 | Standard chat |
| `rich` | ~4 000–8 000 | Deep analysis, test generation |
| `refactor` | ~6 000–12 000 | Refactoring sessions with SUMR.md |

For smaller models (< 8B parameters), use `--profile light` or inject specific sections only.

---

## SUMR.md for Refactoring

`SUMR.md` is a special output optimised for pre-refactoring analysis:

```bash
sumr .           # generates SUMR.md
# or
sumd scan . --fix --profile refactor
```

It includes code complexity metrics, duplication analysis, call-graph hotspots, and evolution history — exactly what an LLM needs to produce a meaningful refactoring plan.

Example prompt:
```
<sumr>
[SUMR.md content]
</sumr>

Based on the analysis above:
1. List the 5 most critical hotspots to refactor.
2. Identify duplicated logic that could be extracted.
3. Suggest a safe refactoring sequence (lower-risk first).
```
