"""SUMD - Structured Unified Markdown Descriptor.

SUMD is a semantic project descriptor format in Markdown that defines intent,
structure, execution entry points, and mental model of a system for both humans and LLMs.
"""

__version__ = "0.3.23"

from sumd.parser import (
    SUMDDocument,
    SUMDParser,
    parse,
    parse_file,
    validate,
    validate_codeblocks,
    validate_markdown,
    validate_sumd_file,
    CodeBlockIssue,
)
from sumd.generator import generate_sumd_content

__all__ = [
    "SUMDDocument",
    "SUMDParser",
    "parse",
    "parse_file",
    "validate",
    "validate_codeblocks",
    "validate_markdown",
    "validate_sumd_file",
    "CodeBlockIssue",
    "generate_sumd_content",
]
