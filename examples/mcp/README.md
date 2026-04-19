# examples/mcp/

How to configure and use the SUMD MCP server with LLM agents.

## What is the MCP Server?

The SUMD MCP (Model Context Protocol) server exposes SUMD operations as callable tools
to any MCP-compatible LLM agent. Once configured, your agent can parse, validate, 
query, and generate SUMD documents without manual file operations.

## Available Tools

| Tool | Description |
|------|-------------|
| `parse_sumd` | Parse a SUMD.md file → structured JSON |
| `validate_sumd` | Validate structure → list of errors |
| `export_sumd` | Export to json / yaml / toml / markdown |
| `list_sections` | Return all section names and types |
| `get_section` | Get content of a specific section by name |
| `info_sumd` | Project name, description, section count |
| `generate_sumd` | Generate a new SUMD.md from a JSON payload |

## Files

| File | Description |
|------|-------------|
| `mcp_client.py` | Standalone MCP client for testing all 7 tools |
| `claude_desktop_config.json` | Claude Desktop configuration |
| `cursor_mcp.json` | Cursor IDE configuration |
| `continue_config.json` | Continue.dev configuration |

## Starting the Server

```bash
# Install with MCP deps
pip install sumd[mcp]

# Start the MCP server (stdio transport — required by most MCP clients)
python -m sumd.mcp_server

# Or from a project directory (so relative paths resolve correctly)
cd /path/to/your-project && python -m sumd.mcp_server
```

## Integration Examples

### Claude Desktop

Copy `claude_desktop_config.json` contents to:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sumd": {
      "command": "python",
      "args": ["-m", "sumd.mcp_server"],
      "cwd": "/path/to/your-project"
    }
  }
}
```

After restarting Claude Desktop, you can ask:
- *"Parse the SUMD.md in my project"*
- *"What sections does SUMD.md contain?"*
- *"Get the Intent section from SUMD.md"*

### Cursor IDE

Add to `.cursor/mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "sumd": {
      "command": "python",
      "args": ["-m", "sumd.mcp_server"]
    }
  }
}
```

### Continue.dev

Add to `.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "sumd.mcp_server"]
        }
      }
    ]
  }
}
```

### Windsurf

Add to `.windsurf/mcp.json`:

```json
{
  "mcpServers": {
    "sumd": {
      "command": "python",
      "args": ["-m", "sumd.mcp_server"]
    }
  }
}
```

## Test the Server

```bash
# Run the standalone client to test all 7 tools
python examples/mcp/mcp_client.py SUMD.md
```
