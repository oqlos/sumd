"""SUMD Generator — compatibility shim.

All logic has been moved to focused modules:
  sumd.toon_parser  — parse *.testql.toon.yaml scenario files
  sumd.extractor    — extract metadata from project source files
  sumd.renderer     — render SUMD.md content

This module re-exports everything for backwards compatibility.
"""

from sumd.toon_parser import *  # noqa: F401,F403
from sumd.extractor import *  # noqa: F401,F403
from sumd.renderer import *  # noqa: F401,F403

# Explicit re-exports for type checkers and direct imports
