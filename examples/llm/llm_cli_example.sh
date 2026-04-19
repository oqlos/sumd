#!/usr/bin/env bash
# examples/llm/llm_cli_example.sh
# Uses simon-willison/llm CLI for SUMD context injection.
#
# Prerequisites:
#   pip install llm
#   llm keys set openai   # or configure another provider
#
# Usage:
#   bash examples/llm/llm_cli_example.sh
#   bash examples/llm/llm_cli_example.sh SUMD.md

set -euo pipefail

SUMD_FILE="${1:-SUMD.md}"

if [[ ! -f "$SUMD_FILE" ]]; then
  echo "Error: $SUMD_FILE not found. Run 'sumd scan . --fix' first." >&2
  exit 1
fi

if ! command -v llm &>/dev/null; then
  echo "Error: llm not found. Run: pip install llm" >&2
  exit 1
fi

echo "=== Pattern 1: Project summary ==="
llm -s "$(cat "$SUMD_FILE")" "Summarise this project in 3 bullet points."

echo ""
echo "=== Pattern 2: Refactoring advice ==="
llm -s "$(cat "$SUMD_FILE")" "Identify the top 3 areas to refactor and explain why."

echo ""
echo "=== Pattern 3: Missing tests ==="
llm -s "$(cat "$SUMD_FILE")" "Based on the API spec and existing testql scenarios, what test coverage is missing?"
