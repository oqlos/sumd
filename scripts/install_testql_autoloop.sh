#!/usr/bin/env bash

set -euo pipefail

TARGET_DIR="${1:-$PWD}"
TARGET_DIR="$(realpath "$TARGET_DIR")"

log() {
  printf '%s\n' "$1"
}

write_if_missing() {
  local path="$1"
  local content="$2"

  if [ -f "$path" ]; then
    log "↷ skip (exists): $path"
    return
  fi

  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" > "$path"
  log "✓ created: $path"
}

log "== TestQL autoloop installer =="
log "Target: $TARGET_DIR"

mkdir -p \
  "$TARGET_DIR/.testql/schemas" \
  "$TARGET_DIR/.testql/reports" \
  "$TARGET_DIR/.aider/prompts" \
  "$TARGET_DIR/.windsurf/workflows"

write_if_missing "$TARGET_DIR/.testql/autoloop-state.json" '{
  "iteration": 0,
  "phase": "bootstrap",
  "current_focus": "discover",
  "history": [],
  "stabilization": {
    "required_consecutive_passes": 2,
    "consecutive_passes": 0
  },
  "quality_gates": {
    "coverage_min": 65,
    "vallm_pass_min": 60,
    "cc_max": 10
  }
}'

write_if_missing "$TARGET_DIR/.testql/schemas/llm-decision.schema.json" '{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TestQLAutoloopDecision",
  "type": "object",
  "additionalProperties": false,
  "required": ["decision", "reason_code", "next_actions", "metrics", "confidence", "risk_score"],
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["generate_tests", "refactor_code", "rerun_tests", "stabilized"]
    },
    "reason_code": {
      "type": "string",
      "minLength": 3
    },
    "next_actions": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "minLength": 3}
    },
    "metrics": {
      "type": "object",
      "additionalProperties": false,
      "required": ["coverage", "vallm", "cc_max"],
      "properties": {
        "coverage": {"type": "number"},
        "vallm": {"type": "number"},
        "cc_max": {"type": "number"}
      }
    },
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "risk_score": {"type": "number", "minimum": 0, "maximum": 1}
  }
}'

write_if_missing "$TARGET_DIR/.aider/Dockerfile" 'FROM python:3.12-slim

WORKDIR /workspace

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir aider-chat

ENTRYPOINT ["aider"]'

write_if_missing "$TARGET_DIR/.aider/docker-compose.yml" 'services:
  aider:
    build:
      context: ..
      dockerfile: .aider/Dockerfile
    working_dir: /workspace
    volumes:
      - ..:/workspace
    env_file:
      - ../.env.testql.autoloop
    stdin_open: true
    tty: true
    command: ["--yes", "--message-file", ".aider/prompts/testql-autoloop.md"]'

write_if_missing "$TARGET_DIR/.aider/prompts/testql-autoloop.md" 'Goal: perform one TestQL autoloop iteration.

Required behavior:
1) Read .testql/autoloop-state.json and .testql/reports/test-run.json.
2) Decide one action: generate_tests | refactor_code | rerun_tests | stabilized.
3) Apply minimal code or test changes based on current failures.
4) Write JSON decision to .testql/reports/llm-decision.json.
5) Increment iteration in .testql/autoloop-state.json.

Constraints:
- Keep edits focused and deterministic.
- Do not invent files outside project scope unless necessary for tests.
- Produce valid JSON matching .testql/schemas/llm-decision.schema.json.'

write_if_missing "$TARGET_DIR/.windsurf/workflows/testql-autoloop.md" '---
description: Run one TestQL + aider autoloop iteration
---
1. Ensure `.env.testql.autoloop` exists with `OPENROUTER_API_KEY`, `AIDER_MODEL_PRIMARY`, and `AIDER_MODEL_FALLBACK`.
2. Generate topology JSON: `testql topology . --format json > .testql/reports/topology.json`.
3. Run test scenario to JSON: `testql run testql-scenarios/generated-cli-tests.testql.toon.yaml --output json > .testql/reports/test-run.json`.
4. Run aider in Docker: `docker compose -f .aider/docker-compose.yml run --rm aider`.
5. Validate decision JSON: `python -m jsonschema -i .testql/reports/llm-decision.json .testql/schemas/llm-decision.schema.json`.
6. If quality gates pass in 2 consecutive iterations, stop. Otherwise loop from step 2.'

write_if_missing "$TARGET_DIR/.windsurf/workflows/testql-model-smoke.md" '---
description: Smoke test Windsurf MCP loop with KIMI and SWE models
---
1. Set `AIDER_MODEL_PRIMARY` to your KIMI 2.6 model id and run one full autoloop iteration.
2. Save output as `.testql/reports/llm-decision.kimi.json`.
3. Set `AIDER_MODEL_PRIMARY` to your SWE 1.6 model id and run one full autoloop iteration.
4. Save output as `.testql/reports/llm-decision.swe.json`.
5. Validate both files against `.testql/schemas/llm-decision.schema.json`.
6. Compare `decision`, `reason_code`, `confidence`, and `risk_score` across models.'

write_if_missing "$TARGET_DIR/.env.testql.autoloop.example" 'OPENROUTER_API_KEY=<your-openrouter-key>
AIDER_MODEL_PRIMARY=openrouter/kimi-k2:free
AIDER_MODEL_FALLBACK=openrouter/swe-1.6:free
AIDER_EDIT_FORMAT=diff
'

write_if_missing "$TARGET_DIR/.testql/reports/.gitkeep" ''

log ""
log "Done. Next steps:"
log "1) cd $TARGET_DIR"
log "2) cp .env.testql.autoloop.example .env.testql.autoloop"
log "3) fill OPENROUTER_API_KEY + model ids"
log "4) docker compose -f .aider/docker-compose.yml run --rm aider"
