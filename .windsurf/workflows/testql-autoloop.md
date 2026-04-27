---
description: Run one TestQL + aider autoloop iteration
---
1. Ensure `.env.testql.autoloop` exists with `OPENROUTER_API_KEY`, `AIDER_MODEL_PRIMARY`, and `AIDER_MODEL_FALLBACK`.
2. Generate topology JSON: `testql topology . --format json > .testql/reports/topology.json`.
3. Run test scenario to JSON: `testql run testql-scenarios/generated-cli-tests.testql.toon.yaml --output json > .testql/reports/test-run.json`.
4. Run aider in Docker: `docker compose -f .aider/docker-compose.yml run --rm aider`.
5. Validate decision JSON: `python -m jsonschema -i .testql/reports/llm-decision.json .testql/schemas/llm-decision.schema.json`.
6. If quality gates pass in 2 consecutive iterations, stop. Otherwise loop from step 2.
