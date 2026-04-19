"""
examples/mcp/mcp_client.py
Standalone client that exercises all 7 SUMD MCP tools via stdio transport.

Usage:
    python examples/mcp/mcp_client.py
    python examples/mcp/mcp_client.py /path/to/SUMD.md
    python examples/mcp/mcp_client.py SUMD.md --tool get_section --args '{"section": "Intent"}'

Prerequisites:
    pip install sumd[mcp]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


async def run(sumd_file: Path, single_tool: str | None = None, tool_args: dict | None = None) -> None:
    try:
        import mcp.client.stdio as stdio_client
        import mcp.types as types
        from mcp import ClientSession, StdioServerParameters
    except ImportError:
        print("Error: MCP client not available. Run: pip install sumd[mcp]")
        sys.exit(1)

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "sumd.mcp_server"],
    )

    async with stdio_client.stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools ({len(tools.tools)}):")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description[:60]}...")
            print()

            if single_tool and tool_args is not None:
                # Run a single tool
                result = await session.call_tool(single_tool, tool_args)
                print(f"=== {single_tool} ===")
                for content in result.content:
                    print(content.text)
                return

            file_str = str(sumd_file.resolve())

            # ── Tool 1: info_sumd ─────────────────────────────────────────────
            print("=== info_sumd ===")
            result = await session.call_tool("info_sumd", {"file": file_str})
            print(result.content[0].text)
            print()

            # ── Tool 2: list_sections ─────────────────────────────────────────
            print("=== list_sections ===")
            result = await session.call_tool("list_sections", {"file": file_str})
            sections = json.loads(result.content[0].text)
            for s in sections:
                print(f"  {s['name']} ({s['type']})")
            print()

            # ── Tool 3: get_section ───────────────────────────────────────────
            if sections:
                first_section = sections[0]["name"]
                print(f"=== get_section ({first_section}) ===")
                result = await session.call_tool("get_section", {"file": file_str, "section": first_section})
                data = json.loads(result.content[0].text)
                # Print first 200 chars of content
                print(data["content"][:200] + ("..." if len(data["content"]) > 200 else ""))
                print()

            # ── Tool 4: validate_sumd ─────────────────────────────────────────
            print("=== validate_sumd ===")
            result = await session.call_tool("validate_sumd", {"file": file_str})
            data = json.loads(result.content[0].text)
            print(f"  valid: {data['valid']}")
            if data["errors"]:
                for e in data["errors"]:
                    print(f"  error: {e}")
            print()

            # ── Tool 5: export_sumd (JSON) ────────────────────────────────────
            print("=== export_sumd (json, first 300 chars) ===")
            result = await session.call_tool("export_sumd", {"file": file_str, "format": "json"})
            print(result.content[0].text[:300] + "...")
            print()

            # ── Tool 6: parse_sumd ────────────────────────────────────────────
            print("=== parse_sumd (project_name + section count) ===")
            result = await session.call_tool("parse_sumd", {"file": file_str})
            data = json.loads(result.content[0].text)
            print(f"  project_name: {data['project_name']}")
            print(f"  sections: {len(data['sections'])}")
            print()

            # ── Tool 7: generate_sumd ─────────────────────────────────────────
            print("=== generate_sumd (in-memory) ===")
            payload = {
                "project_name": "demo-project",
                "description": "A demo project generated via MCP",
                "sections": [
                    {"name": "Intent", "type": "intent", "content": "Demonstrate SUMD MCP tools.", "level": 2}
                ],
            }
            result = await session.call_tool("generate_sumd", {"data": payload})
            print(result.content[0].text[:300])
            print()

            print("=== All 7 MCP tools tested successfully ===")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test SUMD MCP server tools")
    parser.add_argument("file", nargs="?", default="SUMD.md", help="Path to SUMD.md")
    parser.add_argument("--tool", help="Run a single tool by name")
    parser.add_argument("--args", help="JSON arguments for the tool", default="{}")
    args = parser.parse_args()

    sumd_path = Path(args.file)
    if not sumd_path.exists():
        print(f"Error: {sumd_path} not found. Run 'sumd scan . --fix' first.")
        sys.exit(1)

    tool_args = json.loads(args.args) if args.tool else None
    asyncio.run(run(sumd_path, args.tool, tool_args))


if __name__ == "__main__":
    main()
