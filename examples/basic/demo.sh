#!/usr/bin/env bash
# examples/basic/demo.sh
# Demonstrates core sumd and sumr CLI commands.
# Run from the repository root: bash examples/basic/demo.sh

set -euo pipefail

PROJECT="${1:-./examples/basic/sample-project}"

echo "=== SUMD Basic Demo ==="
echo "Target project: $PROJECT"
echo ""

# ── Step 1: Scan — generate SUMD.md ──────────────────────────────────────────
echo "[1/6] Generating SUMD.md (profile: rich)..."
sumd scan "$PROJECT" --fix --profile rich
echo "      → $PROJECT/SUMD.md created"
echo ""

# ── Step 2: Lint — validate the generated file ───────────────────────────────
echo "[2/6] Linting SUMD.md..."
sumd lint "$PROJECT/SUMD.md" && echo "      → valid" || echo "      → validation warnings (see above)"
echo ""

# ── Step 3: Info — show project summary ──────────────────────────────────────
echo "[3/6] Project info:"
sumd info "$PROJECT/SUMD.md"
echo ""

# ── Step 4: Export — convert to JSON ─────────────────────────────────────────
echo "[4/6] Exporting to JSON..."
sumd export "$PROJECT/SUMD.md" --format json --output "$PROJECT/sumd-export.json"
echo "      → $PROJECT/sumd-export.json"
echo ""

# ── Step 5: Map — generate static code map ───────────────────────────────────
echo "[5/6] Generating code map..."
sumd map "$PROJECT" --stdout | head -20
echo "      (output truncated to 20 lines)"
echo ""

# ── Step 6: sumr — generate SUMR.md (refactor analysis) ─────────────────────
echo "[6/6] Generating SUMR.md (refactor profile)..."
sumr "$PROJECT" --fix 2>/dev/null || sumd scan "$PROJECT" --fix --profile refactor
echo "      → $PROJECT/SUMR.md created"

echo ""
echo "=== Done. Files generated ==="
ls -1 "$PROJECT"/*.md "$PROJECT"/*.json 2>/dev/null || true
