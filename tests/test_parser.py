"""Tests for SUMD parser."""

from sumd.parser import SUMDParser, parse, validate


SAMPLE_SUMD = """# doql - Declarative Object Query Language

## Intent

doql provides a declarative language for querying and manipulating structured data.

## Architecture

### System Overview
doql consists of a parser, interpreter, and multiple backend adapters.

### Components
- **Parser**: Converts doql syntax into AST
- **Interpreter**: Executes AST against data sources

## Interfaces

### API
- **Endpoint**: POST /api/v1/query
  - **Description**: Execute doql query

### CLI
- **Command**: `doql query [file]`
  - **Description**: Execute doql query from file

## Workflows

### Query Execution
- **Trigger**: manual
- **Steps**:
  1. Parse query file
  2. Connect to data source
"""


def test_parse_basic():
    """Test basic parsing of SUMD document."""
    document = parse(SAMPLE_SUMD)

    assert document.project_name == "doql"
    assert "Declarative Object Query Language" in document.description
    assert len(document.sections) > 0


def test_parse_sections():
    """Test section parsing."""
    document = parse(SAMPLE_SUMD)

    section_names = {section.name for section in document.sections}
    assert "intent" in section_names
    assert "architecture" in section_names
    assert "interfaces" in section_names
    assert "workflows" in section_names


def test_validate_valid_document():
    """Test validation of valid document."""
    document = parse(SAMPLE_SUMD)
    errors = validate(document)

    assert len(errors) == 0


def test_validate_missing_intent():
    """Test validation fails without intent section."""
    invalid_sumd = """# test

## Architecture

Test architecture.
"""
    document = parse(invalid_sumd)
    errors = validate(document)

    assert len(errors) > 0
    assert any("Intent" in error for error in errors)


def test_parse_file(tmp_path):
    """Test parsing from file."""
    sumd_file = tmp_path / "test.sumd.md"
    sumd_file.write_text(SAMPLE_SUMD)

    from sumd.parser import parse_file

    document = parse_file(sumd_file)

    assert document.project_name == "doql"


def test_parser_class():
    """Test SUMDParser class directly."""
    parser = SUMDParser()
    document = parser.parse(SAMPLE_SUMD)

    assert document.project_name == "doql"
    assert parser.validate(document) == []


def test_markpact_semantic_kinds_valid():
    """All Phase 2 semantic markpact kinds must pass validation."""
    from sumd.parser import validate_codeblocks

    semantic_kinds = {
        "doql": ("less", "app { name: test; }"),
        "openapi": ("yaml", "openapi: '3.0'\ninfo:\n  title: T\n  version: '1'"),
        "testql": ("toon", "HEALTH:\n  - check: alive"),
        "taskfile": (
            "yaml",
            "version: '3'\ntasks:\n  build:\n    cmds:\n      - echo ok",
        ),
        "pyqual": ("yaml", "name: pipeline\nstages: []"),
        "analysis": ("text", "some analysis content"),
    }
    for kind, (lang, body) in semantic_kinds.items():
        block = f"```{lang} markpact:{kind} path=test.file\n{body}\n```"
        issues = validate_codeblocks(block)
        errors = [i for i in issues if i.kind == "error"]
        assert errors == [], f"markpact:{kind} produced errors: {errors}"


def test_markpact_unknown_kind_error():
    """Unknown markpact kind must produce an error."""
    from sumd.parser import validate_codeblocks

    block = "```yaml markpact:unknown path=x.yaml\nkey: val\n```"
    issues = validate_codeblocks(block)
    assert any(
        i.kind == "error" and "unknown markpact kind" in i.message for i in issues
    )


def test_markpact_missing_path_error():
    """Semantic kinds with missing path= must produce an error."""
    from sumd.parser import validate_codeblocks

    block = "```yaml markpact:openapi\nkey: val\n```"
    issues = validate_codeblocks(block)
    assert any(i.kind == "error" and "requires path=" in i.message for i in issues)
