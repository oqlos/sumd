#!/usr/bin/env python3
"""Convenience wrapper — delegates to `sumd scan`.

Usage:
    python sumd/scripts/generate_all_sumd.py [workspace_dir]

Equivalent to:
    sumd scan [workspace_dir] --fix --report sumd-validation-report.json
"""

import subprocess
import sys
from pathlib import Path

workspace = (
    sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent.parent)
)

subprocess.run(
    ["sumd", "scan", workspace, "--fix", "--report", "sumd-validation-report.json"],
    check=True,
)
