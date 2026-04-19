"""Tests for sumd MCP server tools (unit tests using asyncio, no real MCP transport)."""

import asyncio
import json
import textwrap
from pathlib import Path

import pytest

from sumd.mcp_server import (
    _doc_to_dict,
    _resolve_path,
    _TOOL_HANDLERS,
    list_tools,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_SUMD = textwrap.dedent("""\
    # mcpapp

    ## Metadata

    | Key         | Value          |
    |-------------|----------------|
    | version     | 1.0.0          |
    | description | MCP test app   |

    ## Intent

    Expose SUMD tools over MCP protocol.

    ## Architecture

    Single-tier MCP server.

    ## Interfaces

    MCP over stdio.
""")


@pytest.fixture
def sumd_file(tmp_path):
    f = tmp_path / "SUMD.md"
    f.write_text(VALID_SUMD)
    return f


def run(coro):
    """Run a coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestDocToDict:
    def test_has_required_keys(self, sumd_file):
        from sumd.parser import parse_file
        doc = parse_file(sumd_file)
        d = _doc_to_dict(doc)
        assert "project_name" in d
        assert "description" in d
        assert "sections" in d
        assert isinstance(d["sections"], list)

    def test_section_has_fields(self, sumd_file):
        from sumd.parser import parse_file
        doc = parse_file(sumd_file)
        d = _doc_to_dict(doc)
        if d["sections"]:
            sec = d["sections"][0]
            assert "name" in sec
            assert "type" in sec
            assert "content" in sec
            assert "level" in sec


class TestResolvePath:
    def test_absolute_path_unchanged(self, tmp_path):
        p = tmp_path / "file.md"
        result = _resolve_path(str(p))
        assert result == p

    def test_relative_resolves_from_cwd(self):
        result = _resolve_path("SUMD.md")
        assert result.is_absolute()
        assert result.name == "SUMD.md"


# ---------------------------------------------------------------------------
# Tool listing
# ---------------------------------------------------------------------------


class TestListTools:
    def test_returns_seven_tools(self):
        tools = run(list_tools())
        assert len(tools) == 7

    def test_tool_names(self):
        tools = run(list_tools())
        names = {t.name for t in tools}
        expected = {
            "parse_sumd", "validate_sumd", "export_sumd",
            "list_sections", "get_section", "info_sumd", "generate_sumd",
        }
        assert names == expected

    def test_each_tool_has_input_schema(self):
        tools = run(list_tools())
        for t in tools:
            assert t.inputSchema is not None


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


class TestParseSumd:
    def test_returns_json(self, sumd_file):
        result = run(_TOOL_HANDLERS["parse_sumd"]({"file": str(sumd_file)}))
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["project_name"] == "mcpapp"

    def test_missing_file_returns_error(self, tmp_path):
        from sumd.mcp_server import call_tool
        result = run(call_tool("parse_sumd", {"file": str(tmp_path / "no.md")}))
        assert "Error" in result[0].text


class TestValidateSumd:
    def test_valid_file(self, sumd_file):
        result = run(_TOOL_HANDLERS["validate_sumd"]({"file": str(sumd_file)}))
        data = json.loads(result[0].text)
        assert "valid" in data
        assert isinstance(data["errors"], list)

    def test_missing_file_returns_error(self, tmp_path):
        from sumd.mcp_server import call_tool
        result = run(call_tool("validate_sumd", {"file": str(tmp_path / "no.md")}))
        assert "Error" in result[0].text


class TestExportSumd:
    def test_export_json(self, sumd_file):
        result = run(_TOOL_HANDLERS["export_sumd"]({"file": str(sumd_file), "format": "json"}))
        data = json.loads(result[0].text)
        assert "project_name" in data

    def test_export_markdown(self, sumd_file):
        result = run(_TOOL_HANDLERS["export_sumd"]({"file": str(sumd_file), "format": "markdown"}))
        assert "#" in result[0].text

    def test_export_to_file(self, sumd_file, tmp_path):
        out = tmp_path / "out.json"
        result = run(_TOOL_HANDLERS["export_sumd"]({
            "file": str(sumd_file), "format": "json", "output": str(out)
        }))
        assert out.exists()
        assert "Exported" in result[0].text


class TestListSections:
    def test_returns_list(self, sumd_file):
        result = run(_TOOL_HANDLERS["list_sections"]({"file": str(sumd_file)}))
        sections = json.loads(result[0].text)
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_section_has_name(self, sumd_file):
        result = run(_TOOL_HANDLERS["list_sections"]({"file": str(sumd_file)}))
        sections = json.loads(result[0].text)
        assert all("name" in s for s in sections)


class TestGetSection:
    def test_found_section(self, sumd_file):
        result = run(_TOOL_HANDLERS["get_section"]({"file": str(sumd_file), "section": "Intent"}))
        data = json.loads(result[0].text)
        assert data["name"].lower() == "intent"

    def test_missing_section(self, sumd_file):
        result = run(_TOOL_HANDLERS["get_section"]({"file": str(sumd_file), "section": "Nonexistent"}))
        assert "not found" in result[0].text.lower()


class TestInfoSumd:
    def test_returns_info(self, sumd_file):
        result = run(_TOOL_HANDLERS["info_sumd"]({"file": str(sumd_file)}))
        data = json.loads(result[0].text)
        assert data["project_name"] == "mcpapp"
        assert "section_count" in data
        assert isinstance(data["section_types"], list)


class TestGenerateSumd:
    def test_generate_content(self):
        payload = {
            "data": {
                "project_name": "gen-test",
                "description": "Generated",
                "sections": [{"name": "Overview", "level": 2, "content": "Hello"}],
            }
        }
        result = run(_TOOL_HANDLERS["generate_sumd"](payload))
        assert "gen-test" in result[0].text
        assert "Overview" in result[0].text

    def test_generate_to_file(self, tmp_path):
        out = tmp_path / "OUT.md"
        payload = {
            "data": {"project_name": "x", "sections": []},
            "output": str(out),
        }
        result = run(_TOOL_HANDLERS["generate_sumd"](payload))
        assert out.exists()
        assert "Generated" in result[0].text


class TestUnknownTool:
    def test_unknown_returns_error(self):
        from sumd.mcp_server import call_tool
        result = run(call_tool("no_such_tool", {}))
        assert "Unknown tool" in result[0].text
