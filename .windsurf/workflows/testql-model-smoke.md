---
description: Smoke test Windsurf MCP loop with KIMI and SWE models
---
1. Set `AIDER_MODEL_PRIMARY` to your KIMI 2.6 model id and run one full autoloop iteration.
2. Save output as `.testql/reports/llm-decision.kimi.json`.
3. Set `AIDER_MODEL_PRIMARY` to your SWE 1.6 model id and run one full autoloop iteration.
4. Save output as `.testql/reports/llm-decision.swe.json`.
5. Validate both files against `.testql/schemas/llm-decision.schema.json`.
6. Compare `decision`, `reason_code`, `confidence`, and `risk_score` across models.
