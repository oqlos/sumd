# examples/basic/

Demonstrates core `sumd` and `sumr` CLI commands on a minimal sample FastAPI project.

## Files

| File | Description |
|------|-------------|
| `demo.sh` | Shell script running all 6 steps |
| `sample-project/pyproject.toml` | Minimal Python project |
| `sample-project/openapi.yaml` | OpenAPI 3.1 spec with 4 endpoints |
| `sample-project/goal.yaml` | Project intent |

## Run the Demo

```bash
# From the sumd repo root
bash examples/basic/demo.sh

# Or target your own project
bash examples/basic/demo.sh /path/to/your-project
```

## What Happens

1. `sumd scan` → generates `SUMD.md` with rich profile
2. `sumd lint` → validates the generated file  
3. `sumd info` → prints project name + section list
4. `sumd export` → exports to `sumd-export.json`
5. `sumd map` → prints code map (first 20 lines)
6. `sumr` / `sumd scan --profile refactor` → generates `SUMR.md`

## Expected Output

```
=== SUMD Basic Demo ===
Target project: ./examples/basic/sample-project

[1/6] Generating SUMD.md (profile: rich)...
      → ./examples/basic/sample-project/SUMD.md created

[2/6] Linting SUMD.md...
      → valid

[3/6] Project info:
📦 Project: my-api
📝 Description: ...
📑 Sections: 8
  - Metadata (metadata)
  - Architecture (architecture)
  ...
```

## Manual Commands

```bash
PROJECT=./examples/basic/sample-project

# Generate SUMD.md
sumd scan $PROJECT --fix

# Generate with minimal profile (faster, fewer tokens)
sumd scan $PROJECT --fix --profile minimal

# Generate SUMR.md
sumr $PROJECT

# Generate testql scenario skeletons from openapi.yaml
sumd scaffold $PROJECT

# Validate
sumd lint $PROJECT/SUMD.md

# Export to YAML
sumd export $PROJECT/SUMD.md --format yaml

# Extract a single section
sumd extract $PROJECT/SUMD.md --section Architecture
```
