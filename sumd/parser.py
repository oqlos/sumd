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


# Backward-compatible re-exports from validator module
from sumd.validator import (
    CodeBlockIssue,
    validate_codeblocks,
    validate_markdown,
    validate_sumd_file,
)
