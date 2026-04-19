"""SUMD Parser - Parse and validate SUMD markdown documents."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SectionType(Enum):
    """SUMD section types."""

    PROJECT_HEADER = "project_header"
    METADATA = "metadata"
    INTENT = "intent"
    ARCHITECTURE = "architecture"
    INTERFACES = "interfaces"
    WORKFLOWS = "workflows"
    CONFIGURATION = "configuration"
    DEPENDENCIES = "dependencies"
    DEPLOYMENT = "deployment"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a SUMD section."""

    name: str
    type: SectionType
    content: str
    level: int
    subsections: List["Section"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SUMDDocument:
    """Represents a parsed SUMD document."""

    project_name: str
    description: str
    sections: List[Section] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""


class SUMDParser:
    """Parser for SUMD markdown documents."""

    SECTION_MAPPING = {
        "metadata": SectionType.METADATA,
        "intent": SectionType.INTENT,
        "architecture": SectionType.ARCHITECTURE,
        "interfaces": SectionType.INTERFACES,
        "workflows": SectionType.WORKFLOWS,
        "configuration": SectionType.CONFIGURATION,
        "dependencies": SectionType.DEPENDENCIES,
        "deployment": SectionType.DEPLOYMENT,
    }

    def __init__(self):
        self.current_document: Optional[SUMDDocument] = None

    def parse(self, content: str) -> SUMDDocument:
        """Parse a SUMD markdown document.

        Args:
            content: The markdown content to parse

        Returns:
            SUMDDocument: Parsed document structure
        """
        self.current_document = SUMDDocument(
            project_name="", description="", raw_content=content
        )

        lines = content.split("\n")
        self._parse_header(lines)
        self._parse_sections(lines)

        return self.current_document

    def parse_file(self, path: Path) -> SUMDDocument:
        """Parse a SUMD file.

        Args:
            path: Path to the SUMD markdown file

        Returns:
            SUMDDocument: Parsed document structure
        """
        content = path.read_text(encoding="utf-8")
        return self.parse(content)

    def _parse_header(self, lines: List[str]) -> None:
        """Parse the project header (H1).

        Args:
            lines: List of document lines
        """
        if not lines:
            return

        # Find H1 header
        for i, line in enumerate(lines):
            if line.startswith("# ") and not line.startswith("##"):
                header_content = line[2:].strip()
                # Split into name and description
                parts = header_content.split(" - ", 1)
                self.current_document.project_name = parts[0].strip()
                if len(parts) > 1:
                    self.current_document.description = parts[1].strip()
                else:
                    # Look for description on next lines
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            self.current_document.description = lines[j].strip()
                            break
                break

    def _parse_sections(self, lines: List[str]) -> None:
        """Parse all sections in the document.

        Args:
            lines: List of document lines
        """
        sections = []
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith("##"):
                # Save previous section
                if current_section:
                    current_section.content = "\n".join(current_content).strip()
                    sections.append(current_section)
                    current_content = []

                # Start new section
                section_name = line[2:].strip().lower()
                section_type = self.SECTION_MAPPING.get(
                    section_name, SectionType.UNKNOWN
                )
                current_section = Section(
                    name=section_name, type=section_type, content="", level=2
                )
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = "\n".join(current_content).strip()
            sections.append(current_section)

        self.current_document.sections = sections

    def validate(self, document: SUMDDocument) -> List[str]:
        """Validate a SUMD document against the specification.

        Args:
            document: The document to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required sections
        section_types = {section.type for section in document.sections}

        if SectionType.INTENT not in section_types:
            errors.append("Missing required section: Intent")

        if SectionType.ARCHITECTURE not in section_types:
            errors.append("Missing required section: Architecture")

        if SectionType.INTERFACES not in section_types:
            errors.append("Missing required section: Interfaces")

        # Check project name
        if not document.project_name:
            errors.append("Missing project name in header")

        return errors


def parse(content: str) -> SUMDDocument:
    """Parse a SUMD markdown document.

    Args:
        content: The markdown content to parse

    Returns:
        SUMDDocument: Parsed document structure
    """
    parser = SUMDParser()
    return parser.parse(content)


def parse_file(path: Path) -> SUMDDocument:
    """Parse a SUMD file.

    Args:
        path: Path to the SUMD markdown file

    Returns:
        SUMDDocument: Parsed document structure
    """
    parser = SUMDParser()
    return parser.parse_file(path)


def validate(document: SUMDDocument) -> List[str]:
    """Validate a SUMD document.

    Args:
        document: The document to validate

    Returns:
        List of validation errors (empty if valid)
    """
    parser = SUMDParser()
    return parser.validate(document)


# ---------------------------------------------------------------------------
# Codeblock format validators
# ---------------------------------------------------------------------------

_CODEBLOCK_RE = re.compile(
    r"^```(?P<lang>\w+)(?:[ \t]+(?P<meta>[^\n]*))?$\n(?P<body>[\s\S]*?)\n^```[ \t]*$",
    re.MULTILINE,
)

_MARKPACT_META_RE = re.compile(r"markpact:(?P<kind>\w+)(?:[ \t]+(?P<attrs>.*))?")


@dataclass
class CodeBlockIssue:
    line: int
    lang: str
    kind: str  # 'error' | 'warning'
    message: str
    meta: str = ""


def _validate_yaml_body(body: str, path: str) -> list[str]:
    """Check YAML body is parseable."""
    try:
        import yaml

        yaml.safe_load(body)
        return []
    except Exception as e:
        return [f"invalid YAML in {path}: {e}"]


def _validate_less_css_body(body: str, path: str) -> list[str]:
    """Basic sanity: balanced braces."""
    opens = body.count("{")
    closes = body.count("}")
    if opens != closes:
        return [f"unbalanced braces in {path}: {opens} open vs {closes} close"]
    return []


def _validate_mermaid_body(body: str, path: str) -> list[str]:
    """Check mermaid block starts with a valid diagram type."""
    first = body.strip().split("\n")[0].strip()
    valid_starts = (
        "flowchart",
        "graph",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "erDiagram",
        "gantt",
        "pie",
        "journey",
    )
    if not any(first.startswith(s) for s in valid_starts):
        return [f"mermaid block in {path} has unknown diagram type: {first!r}"]
    return []


def _validate_toon_body(body: str, path: str) -> list[str]:
    """Check toon block has at least one recognised section header."""
    headers = re.findall(r"^[A-Z_]+(?:\[.*?\])?(?:\{.*?\})?:", body, re.MULTILINE)
    if not headers:
        return [
            f"toon block in {path} has no section headers (e.g. HEALTH, ALERTS, MODULES)"
        ]
    return []


def _validate_bash_body(body: str, path: str) -> list[str]:
    """Check bash block is non-empty and doesn't contain obvious placeholders."""
    if not body.strip():
        return [f"empty bash block in {path}"]
    if "<YOUR_" in body or "TODO" in body:
        return [f"unresolved placeholder in bash block at {path}"]
    return []


def _validate_deps_body(body: str, path: str) -> list[str]:
    """Each line of a deps block should be a valid pip requirement or empty."""
    issues = []
    for i, line in enumerate(body.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # PEP 508 lookalike: name with optional extras/version
        if not re.match(r"^[A-Za-z0-9_\-\.]+", line):
            issues.append(f"deps line {i} in {path} looks invalid: {line!r}")
    return issues


_LANG_VALIDATORS = {
    "yaml": _validate_yaml_body,
    "less": _validate_less_css_body,
    "css": _validate_less_css_body,
    "mermaid": _validate_mermaid_body,
    "toon": _validate_toon_body,
    "bash": _validate_bash_body,
    "text": _validate_deps_body,  # markpact:deps python
}

_VALID_MARKPACT_KINDS = {
    # generic
    "file",
    "deps",
    "run",
    "test",
    "bootstrap",
    "publish",
    # semantic (Phase 2)
    "doql",
    "openapi",
    "testql",
    "taskfile",
    "pyqual",
    "analysis",
}
_MARKPACT_REQUIRED_ATTRS = {
    "file": "path",
    "doql": "path",
    "openapi": "path",
    "testql": "path",
    "taskfile": "path",
    "pyqual": "path",
    "analysis": "path",
}


def validate_codeblocks(content: str, source: str = "SUMD.md") -> list[CodeBlockIssue]:
    """Validate all fenced code blocks in *content*.

    Checks:
    - markpact annotation syntax (kind, required attrs)
    - language-specific body format (yaml parseable, braces balanced, etc.)
    - non-empty bodies
    """
    issues: list[CodeBlockIssue] = []

    for m in _CODEBLOCK_RE.finditer(content):
        lang = (m.group("lang") or "").strip()
        meta = (m.group("meta") or "").strip()
        body = (m.group("body") or "").strip()
        line_no = content[: m.start()].count("\n") + 1
        ctx = f"{source}:{line_no}"

        # ── markpact annotation checks ──────────────────────────────────
        mp = _MARKPACT_META_RE.search(meta)
        if mp:
            kind = mp.group("kind")
            attrs = mp.group("attrs") or ""
            if kind not in _VALID_MARKPACT_KINDS:
                issues.append(
                    CodeBlockIssue(
                        line_no,
                        lang,
                        "error",
                        f"unknown markpact kind {kind!r} (valid: {', '.join(sorted(_VALID_MARKPACT_KINDS))})",
                        meta,
                    )
                )
            req_attr = _MARKPACT_REQUIRED_ATTRS.get(kind)
            if req_attr and f"{req_attr}=" not in attrs:
                issues.append(
                    CodeBlockIssue(
                        line_no,
                        lang,
                        "error",
                        f"markpact:{kind} requires {req_attr}=... but got: {attrs!r}",
                        meta,
                    )
                )

        # ── body emptiness ──────────────────────────────────────────────
        if not body:
            issues.append(
                CodeBlockIssue(
                    line_no, lang, "warning", f"empty code block (lang={lang!r})", meta
                )
            )
            continue

        # ── language-specific body validation ───────────────────────────
        validator = _LANG_VALIDATORS.get(lang)
        if validator:
            for msg in validator(body, ctx):
                issues.append(CodeBlockIssue(line_no, lang, "error", msg, meta))

    return issues


# ---------------------------------------------------------------------------
# Markdown structure validators
# ---------------------------------------------------------------------------

_REQUIRED_H2 = {
    "metadata",
    "intent",
    "architecture",
    "workflows",
    "dependencies",
    "deployment",
}
_REQUIRED_H2_REFACTOR = {"metadata", "architecture", "refactoring analysis"}
_RECOMMENDED_H2 = {"interfaces"}  # present in API projects but not required

_METADATA_FIELDS = {"name", "version"}  # required metadata bullet keys


def _check_h1(lines: list[str], source: str) -> list[str]:
    """Return error if H1 title is missing."""
    if not any(re.match(r"^# [^#]", line) for line in lines):
        return [f"{source}: missing H1 title"]
    return []


def _check_required_sections(
    lines: list[str], source: str, profile: str = "rich"
) -> list[str]:
    """Return errors for any missing required H2 sections."""
    found_h2 = {
        re.sub(r"`.*?`", "", line[3:]).strip().lower()
        for line in lines
        if line.startswith("## ")
    }
    required = _REQUIRED_H2_REFACTOR if profile == "refactor" else _REQUIRED_H2
    return [
        f"{source}: missing required section '## {req.title()}'"
        for req in required
        if not any(req in h for h in found_h2)
    ]


def _check_metadata_fields(lines: list[str], source: str) -> list[str]:
    """Return errors for missing required metadata bullet fields."""
    in_meta = False
    meta_found: set[str] = set()
    for line in lines:
        if line.startswith("## Metadata"):
            in_meta = True
            continue
        if in_meta and line.startswith("## "):
            break
        if in_meta:
            m = re.match(r"- \*\*(\w+)\*\*:", line)
            if m:
                meta_found.add(m.group(1).lower())
    return [
        f"{source}: metadata section missing '**{req}**' field"
        for req in _METADATA_FIELDS
        if req not in meta_found
    ]


def _check_unclosed_fences(lines: list[str], source: str) -> list[str]:
    """Return error if there is an odd number of ``` fence markers."""
    if sum(1 for line in lines if re.match(r"^```", line)) % 2 != 0:
        return [f"{source}: unclosed fenced code block (odd number of ``` markers)"]
    return []


def _check_empty_links(content: str, source: str) -> list[str]:
    """Return errors for markdown links with empty href."""
    return [
        f"{source}: empty link href for [{text}]()"
        for text in re.findall(r"\[([^\]]+)\]\(\s*\)", content)
    ]


def validate_markdown(
    content: str, source: str = "SUMD.md", profile: str = "rich"
) -> list[str]:
    """Validate SUMD markdown structure.

    Checks:
    - H1 title present
    - Required H2 sections present (profile-aware)
    - Metadata section has name and version bullets
    - No broken markdown links [text]() with empty href
    - No unclosed fenced code blocks
    """
    lines = content.splitlines()
    return (
        _check_h1(lines, source)
        + _check_required_sections(lines, source, profile)
        + _check_metadata_fields(lines, source)
        + _check_unclosed_fences(lines, source)
        + _check_empty_links(content, source)
    )


# ---------------------------------------------------------------------------
# Combined validator
# ---------------------------------------------------------------------------


def validate_sumd_file(path: Path, profile: str = "rich") -> dict:
    """Run all validators on a SUMD.md file.

    Returns:
        {
          "source": str,
          "markdown": list[str],        # structural issues
          "codeblocks": list[CodeBlockIssue],  # format issues
          "ok": bool,
        }
    """
    content = path.read_text(encoding="utf-8")
    source = path.name
    md_issues = validate_markdown(content, source, profile)
    cb_issues = validate_codeblocks(content, source)
    return {
        "source": str(path),
        "markdown": md_issues,
        "codeblocks": cb_issues,
        "ok": not md_issues and not any(c.kind == "error" for c in cb_issues),
    }
