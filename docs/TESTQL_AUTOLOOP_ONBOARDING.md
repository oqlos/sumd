# TestQL Autoloop Onboarding (Windsurf MCP + aider)

This guide sets up an autonomous loop for:

1. Generate or update tests.
2. Run tests and quality checks.
3. Ask LLM for next action in strict JSON.
4. Refactor code.
5. Re-run until quality gates are stable.

Target project example used here:

- `/home/tom/github/maskservice/c2004`

## 1) Prerequisites

- Python `>=3.10`
- Docker + Docker Compose
- `git`
- `task` (Taskfile runner)
- Installed tools in project venv:
  - `testql`
  - `pyqual`
  - `aider-chat`

Install in your target project:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install testql pyqual aider-chat jsonschema
```

## 2) Bootstrap files in a new project

From this repository:

```bash
bash scripts/install_testql_autoloop.sh /home/tom/github/maskservice/c2004
```

What the installer creates:

- `.testql/autoloop-state.json`
- `.testql/schemas/llm-decision.schema.json`
- `.testql/reports/.gitkeep`
- `.aider/Dockerfile`
- `.aider/docker-compose.yml`
- `.aider/prompts/testql-autoloop.md`
- `.windsurf/workflows/testql-autoloop.md`
- `.windsurf/workflows/testql-model-smoke.md`
- `.env.testql.autoloop.example`

## 3) Configure models and secrets

In target project:

```bash
cp .env.testql.autoloop.example .env.testql.autoloop
```

Set:

- `OPENROUTER_API_KEY`
- `AIDER_MODEL_PRIMARY` (KIMI 2.6 family)
- `AIDER_MODEL_FALLBACK` (SWE 1.6 family)

Recommended flow:

1. Start with your expected IDs (for example `openrouter/kimi-k2:free`, `openrouter/swe-1.6:free`).
2. Verify exact IDs currently available in your OpenRouter account.
3. Keep fallback model configured to avoid loop interruption.

## 4) Start aider in Docker

```bash
docker compose -f .aider/docker-compose.yml run --rm aider
```

If git safe-directory error appears in container:

```bash
git config --global --add safe.directory /workspace
```

## 5) Run one autoloop iteration manually

In target project root:

```bash
mkdir -p .testql/reports
testql topology . --format json > .testql/reports/topology.json

# Run scenario (replace with your scenario path)
testql run testql-scenarios/generated-cli-tests.testql.toon.yaml --output json > .testql/reports/test-run.json

# Quality snapshot
pyqual run || true
```

Then ask aider (prompt from `.aider/prompts/testql-autoloop.md`) to:

- update/extend tests,
- refactor failing paths,
- write `.testql/reports/llm-decision.json` valid against schema,
- increment `iteration` in `.testql/autoloop-state.json`.

## 6) Windsurf MCP model smoke test scenario

Use workflow `.windsurf/workflows/testql-model-smoke.md`.

Expected result for both models:

- MCP tools available and callable.
- one pass through: topology -> test run -> JSON decision output.
- `llm-decision.json` validates against `.testql/schemas/llm-decision.schema.json`.

Minimal smoke checklist:

1. KIMI model run returns valid JSON decision.
2. SWE model run returns valid JSON decision.
3. `reason_code`, `next_actions`, `metrics`, `confidence`, `risk_score` are present.
4. No malformed JSON or schema mismatch.

## 7) Quality gates and stabilization

Default gates for loop stabilization:

- `coverage >= 65`
- `vallm >= 60`
- `cc_max <= 10`

Stop criteria suggestion:

- 2 consecutive iterations with all gates passing and no new regressions.

## 8) Troubleshooting

- Model `404`/`not found`: switch to currently available OpenRouter model ID.
- Context too large: reduce prompt payload and pass only current failures.
- Aider cannot edit file: ensure file is tracked and not excluded by ignore rules.
- Docker path issues: verify `.aider/docker-compose.yml` build context and mounted workspace path.
