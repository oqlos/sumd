"""SUMD MCP Server — exposes sumd as an MCP service.

Tools exposed:
  - parse_sumd       : parse a SUMD.md file and return structured data
  - validate_sumd    : validate a SUMD.md file and return errors
  - export_sumd      : export SUMD.md to json/yaml/toml/markdown
  - list_sections    : list section names and types from a SUMD document
  - get_section      : retrieve content of a specific section
  - info_sumd        : return project name, description and stats
  - generate_sumd    : generate SUMD.md from a JSON payload
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from sumd.parser import SUMDParser, parse_file

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

server = Server("sumd-mcp")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc_to_dict(doc) -> dict[str, Any]:
    return {
        "project_name": doc.project_name,
        "description": doc.description,
        "sections": [
            {
                "name": s.name,
                "type": s.type.value,
                "content": s.content,
                "level": s.level,
            }
            for s in doc.sections
        ],
    }


def _resolve_path(path: str) -> Path:
    """Resolve path; if relative, resolve from CWD."""
    p = Path(path)
    if not p.is_absolute():
        p = Path(os.getcwd()) / p
    return p


# ---------------------------------------------------------------------------
# Tool listing
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="parse_sumd",
            description="Parse a SUMD.md file and return the full structured document as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file (absolute or relative to CWD).",
                    }
                },
                "required": ["file"],
            },
        ),
        types.Tool(
            name="validate_sumd",
            description="Validate a SUMD.md file. Returns a list of validation errors (empty list = valid).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file.",
                    }
                },
                "required": ["file"],
            },
        ),
        types.Tool(
            name="export_sumd",
            description="Export a SUMD.md file to json, yaml, toml, or markdown format.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file.",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "yaml", "toml", "markdown"],
                        "description": "Output format.",
                        "default": "json",
                    },
                    "output": {
                        "type": "string",
                        "description": "Optional output file path. If omitted, content is returned as string.",
                    },
                },
                "required": ["file"],
            },
        ),
        types.Tool(
            name="list_sections",
            description="List all section names and types in a SUMD document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file.",
                    }
                },
                "required": ["file"],
            },
        ),
        types.Tool(
            name="get_section",
            description="Get the content of a specific section from a SUMD document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file.",
                    },
                    "section": {
                        "type": "string",
                        "description": "Section name or type (e.g. 'Intent', 'intent', 'Dependencies').",
                    },
                },
                "required": ["file", "section"],
            },
        ),
        types.Tool(
            name="info_sumd",
            description="Return project name, description and section statistics for a SUMD document.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the SUMD markdown file.",
                    }
                },
                "required": ["file"],
            },
        ),
        types.Tool(
            name="generate_sumd",
            description="Generate a SUMD.md document from a JSON payload.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "SUMD document data with project_name, description, and sections array.",
                    },
                    "output": {
                        "type": "string",
                        "description": "Optional output file path. If omitted, content is returned as string.",
                    },
                },
                "required": ["data"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

async def _tool_parse_sumd(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    doc = parse_file(path)
    return [types.TextContent(type="text", text=json.dumps(_doc_to_dict(doc), indent=2, ensure_ascii=False))]


async def _tool_validate_sumd(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    doc = parse_file(path)
    parser = SUMDParser()
    errors = parser.validate(doc)
    result = json.dumps({"valid": len(errors) == 0, "errors": errors}, indent=2)
    return [types.TextContent(type="text", text=result)]


async def _tool_export_sumd(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    fmt = arguments.get("format", "json")
    output_path = arguments.get("output")
    doc = parse_file(path)
    data = _doc_to_dict(doc)
    if fmt == "markdown":
        content = doc.raw_content
    elif fmt == "yaml":
        import yaml
        content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    elif fmt == "toml":
        import toml
        content = toml.dumps(data)
    else:
        content = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        out = _resolve_path(output_path)
        out.write_text(content, encoding="utf-8")
        return [types.TextContent(type="text", text=f"Exported to {out}")]
    return [types.TextContent(type="text", text=content)]


async def _tool_list_sections(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    doc = parse_file(path)
    sections = [{"name": s.name, "type": s.type.value, "level": s.level} for s in doc.sections]
    return [types.TextContent(type="text", text=json.dumps(sections, indent=2, ensure_ascii=False))]


async def _tool_get_section(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    query = arguments["section"].lower()
    doc = parse_file(path)
    match = next(
        (s for s in doc.sections if s.name.lower() == query or s.type.value == query),
        None,
    )
    if match is None:
        return [types.TextContent(type="text", text=f'Section "{arguments["section"]}" not found.')]
    result = {"name": match.name, "type": match.type.value, "level": match.level, "content": match.content}
    return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def _tool_info_sumd(arguments: dict) -> list[types.TextContent]:
    path = _resolve_path(arguments["file"])
    doc = parse_file(path)
    info = {
        "project_name": doc.project_name,
        "description": doc.description,
        "section_count": len(doc.sections),
        "section_types": [s.type.value for s in doc.sections],
    }
    return [types.TextContent(type="text", text=json.dumps(info, indent=2, ensure_ascii=False))]


async def _tool_generate_sumd(arguments: dict) -> list[types.TextContent]:
    data = arguments["data"]
    output_path = arguments.get("output")
    lines: list[str] = [f"# {data.get('project_name', 'Project')}", ""]
    if data.get("description"):
        lines += [data["description"], ""]
    for section in data.get("sections", []):
        level = "#" * section.get("level", 2)
        lines += [f"{level} {section['name']}", ""]
        if section.get("content"):
            lines += [section["content"], ""]
    content = "\n".join(lines)
    if output_path:
        out = _resolve_path(output_path)
        out.write_text(content, encoding="utf-8")
        return [types.TextContent(type="text", text=f"Generated {out}")]
    return [types.TextContent(type="text", text=content)]


_TOOL_HANDLERS = {
    "parse_sumd":    _tool_parse_sumd,
    "validate_sumd": _tool_validate_sumd,
    "export_sumd":   _tool_export_sumd,
    "list_sections": _tool_list_sections,
    "get_section":   _tool_get_section,
    "info_sumd":     _tool_info_sumd,
    "generate_sumd": _tool_generate_sumd,
}


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    try:
        handler = _TOOL_HANDLERS.get(name)
        if handler is None:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
        return await handler(arguments)
    except Exception as exc:
        return [types.TextContent(type="text", text=f"Error: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
