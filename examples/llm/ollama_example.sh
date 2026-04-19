#!/usr/bin/env bash
# examples/llm/ollama_example.sh
# Use SUMD.md as context with a local model via Ollama.
#
# Prerequisites:
#   Install Ollama: https://ollama.com/download
#   Pull a model:   ollama pull llama3
#
# Usage:
#   bash examples/llm/ollama_example.sh
#   bash examples/llm/ollama_example.sh SUMD.md "What is the main entry point?"
#   OLLAMA_MODEL=mistral bash examples/llm/ollama_example.sh

set -euo pipefail

SUMD_FILE="${1:-SUMD.md}"
QUESTION="${2:-Summarise this project and list its CLI commands.}"
MODEL="${OLLAMA_MODEL:-llama3}"

if [[ ! -f "$SUMD_FILE" ]]; then
  echo "Error: $SUMD_FILE not found. Run 'sumd scan . --fix' first." >&2
  exit 1
fi

if ! command -v ollama &>/dev/null; then
  echo "Error: ollama not found. Install from https://ollama.com/download" >&2
  exit 1
fi

CONTEXT="$(cat "$SUMD_FILE")"

echo "Model:    $MODEL"
echo "Context:  $SUMD_FILE ($(wc -l < "$SUMD_FILE") lines)"
echo "Question: $QUESTION"
echo "---"

ollama run "$MODEL" "$(printf 'Context:\n\n%s\n\nQuestion: %s' "$CONTEXT" "$QUESTION")"
