"""SUMD - Structured Unified Markdown Descriptor.

SUMD is a semantic project descriptor format in Markdown that defines intent,
structure, execution entry points, and mental model of a system for both humans and LLMs.
"""

__version__ = "0.1.9"

from sumd.parser import (
    SUMDDocument,
    SUMDParser,
    parse,
    parse_file,
    validate,
)

__all__ = [
    "SUMDDocument",
    "SUMDParser",
    "parse",
    "parse_file",
    "validate",
]
