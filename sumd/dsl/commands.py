"""DSL Command Registry for SUMD DSL."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from .engine import DSLContext, DSLEngine


@dataclass
class DSLCommand:
    """DSL command definition."""
    name: str
    description: str
    usage: str
    function: Callable
    aliases: List[str] = None
    category: str = "general"
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class DSLCommandRegistry:
    """Registry for DSL commands."""
    
    def __init__(self):
        self._commands: Dict[str, DSLCommand] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, command: DSLCommand) -> None:
        """Register a DSL command."""
        self._commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self._commands[alias] = command
        
        # Add to category
        if command.category not in self._categories:
            self._categories[command.category] = []
        if command.name not in self._categories[command.category]:
            self._categories[command.category].append(command.name)
    
    def get_command(self, name: str) -> Optional[DSLCommand]:
        """Get a command by name or alias."""
        return self._commands.get(name)
    
    def list_commands(self, category: Optional[str] = None) -> List[DSLCommand]:
        """List all commands, optionally filtered by category."""
        if category:
            command_names = self._categories.get(category, [])
            return [self._commands[name] for name in command_names]
        
        # Return unique commands (skip aliases)
        unique_commands = {}
        for command in self._commands.values():
            if command.name not in unique_commands:
                unique_commands[command.name] = command
        
        return list(unique_commands.values())
    
    def list_categories(self) -> List[str]:
        """List all command categories."""
        return list(self._categories.keys())
    
    def get_help(self, command_name: Optional[str] = None) -> str:
        """Get help for commands."""
        if command_name:
            command = self.get_command(command_name)
            if not command:
                return f"Unknown command: {command_name}"
            
            help_text = f"""
{command.name} - {command.description}

Usage: {command.usage}

Aliases: {', '.join(command.aliases) if command.aliases else 'None'}
Category: {command.category}
            """.strip()
            return help_text
        
        # List all commands
        help_text = "SUMD DSL Commands:\n\n"
        
        for category in self._categories:
            help_text += f"{category.upper()}:\n"
            for cmd_name in self._categories[category]:
                cmd = self._commands[cmd_name]
                help_text += f"  {cmd.name:<15} {cmd.description}\n"
                for alias in cmd.aliases:
                    help_text += f"    {alias:<13} (alias for {cmd.name})\n"
            help_text += "\n"
        
        return help_text.strip()


# Built-in SUMD DSL commands
def create_builtin_registry() -> DSLCommandRegistry:
    """Create registry with built-in commands."""
    registry = DSLCommandRegistry()
    
    # File operations
    registry.register(DSLCommand(
        name="cat",
        description="Display file contents",
        usage="cat <file_path>",
        function=_cmd_cat,
        aliases=["type", "show"],
        category="files"
    ))
    
    registry.register(DSLCommand(
        name="ls",
        description="List directory contents",
        usage="ls [path] [pattern]",
        function=_cmd_ls,
        aliases=["dir", "list"],
        category="files"
    ))
    
    registry.register(DSLCommand(
        name="edit",
        description="Edit a file",
        usage="edit <file_path> <content>",
        function=_cmd_edit,
        aliases=["modify", "update"],
        category="files"
    ))
    
    registry.register(DSLCommand(
        name="mkdir",
        description="Create directory",
        usage="mkdir <dir_path>",
        function=_cmd_mkdir,
        aliases=["md", "create_dir"],
        category="files"
    ))
    
    registry.register(DSLCommand(
        name="rm",
        description="Remove file or directory",
        usage="rm <path>",
        function=_cmd_rm,
        aliases=["del", "remove"],
        category="files"
    ))
    
    # SUMD operations
    registry.register(DSLCommand(
        name="sumd_scan",
        description="Scan project and generate SUMD",
        usage="sumd_scan [path] [options]",
        function=_cmd_sumd_scan,
        aliases=["scan", "analyze"],
        category="sumd"
    ))
    
    registry.register(DSLCommand(
        name="sumd_map",
        description="Generate project map",
        usage="sumd_map [path] [options]",
        function=_cmd_sumd_map,
        aliases=["map", "project_map"],
        category="sumd"
    ))
    
    registry.register(DSLCommand(
        name="sumd_validate",
        description="Validate SUMD document",
        usage="sumd_validate <file_path>",
        function=_cmd_sumd_validate,
        aliases=["validate", "check"],
        category="sumd"
    ))
    
    registry.register(DSLCommand(
        name="sumd_info",
        description="Show SUMD document info",
        usage="sumd_info <file_path>",
        function=_cmd_sumd_info,
        aliases=["info", "document_info"],
        category="sumd"
    ))
    
    # Search operations
    registry.register(DSLCommand(
        name="find",
        description="Find files matching pattern",
        usage="find <pattern> [path]",
        function=_cmd_find,
        aliases=["search", "locate"],
        category="search"
    ))
    
    registry.register(DSLCommand(
        name="grep",
        description="Search for text in files",
        usage="grep <pattern> [files]",
        function=_cmd_grep,
        aliases=["search_text", "find_text"],
        category="search"
    ))
    
    # Utility operations
    registry.register(DSLCommand(
        name="echo",
        description="Display message",
        usage="echo <message>",
        function=_cmd_echo,
        aliases=["print", "say"],
        category="utility"
    ))
    
    registry.register(DSLCommand(
        name="pwd",
        description="Print working directory",
        usage="pwd",
        function=_cmd_pwd,
        aliases=["cwd", "current_dir"],
        category="utility"
    ))
    
    registry.register(DSLCommand(
        name="cd",
        description="Change directory",
        usage="cd <path>",
        function=_cmd_cd,
        aliases=["chdir", "change_dir"],
        category="utility"
    ))
    
    registry.register(DSLCommand(
        name="help",
        description="Show help information",
        usage="help [command]",
        function=_cmd_help,
        aliases=["?", "usage"],
        category="utility"
    ))
    
    registry.register(DSLCommand(
        name="clear",
        description="Clear screen",
        usage="clear",
        function=_cmd_clear,
        aliases=["cls", "reset"],
        category="utility"
    ))
    
    # Variable operations
    registry.register(DSLCommand(
        name="set",
        description="Set variable",
        usage="set <name> <value>",
        function=_cmd_set,
        aliases=["var", "assign"],
        category="variables"
    ))
    
    registry.register(DSLCommand(
        name="get",
        description="Get variable value",
        usage="get <name>",
        function=_cmd_get,
        aliases=["show_var", "value"],
        category="variables"
    ))
    
    registry.register(DSLCommand(
        name="unset",
        description="Remove variable",
        usage="unset <name>",
        function=_cmd_unset,
        aliases=["del_var", "remove_var"],
        category="variables"
    ))
    
    registry.register(DSLCommand(
        name="vars",
        description="List all variables",
        usage="vars",
        function=_cmd_vars,
        aliases=["variables", "list_vars"],
        category="variables"
    ))
    
    registry.register(DSLCommand(
        name="exists",
        description="Check if file exists",
        usage="exists <file_path>",
        function=_cmd_exists,
        category="files"
    ))
    
    registry.register(DSLCommand(
        name="read_file",
        description="Read file contents",
        usage="read_file <file_path>",
        function=_cmd_read_file,
        category="files"
    ))
    
    return registry


# Command implementations
async def _cmd_cat(context: DSLContext, args: List[str]) -> str:
    """Display file contents."""
    if not args:
        raise ValueError("Usage: cat <file_path>")
    
    file_path = context.working_directory / args[0]
    if not file_path.exists():
        raise ValueError(f"File not found: {args[0]}")
    
    return file_path.read_text(encoding="utf-8")


async def _cmd_ls(context: DSLContext, args: List[str]) -> List[str]:
    """List directory contents."""
    path = context.working_directory
    pattern = "*"
    
    if args:
        if len(args) == 1:
            # Could be path or pattern
            test_path = context.working_directory / args[0]
            if test_path.exists() and test_path.is_dir():
                path = test_path
            else:
                pattern = args[0]
        elif len(args) == 2:
            path = context.working_directory / args[0]
            pattern = args[1]
    
    if not path.exists():
        raise ValueError(f"Path not found: {path}")
    
    items = []
    for item in sorted(path.glob(pattern)):
        relative_path = item.relative_to(context.working_directory)
        if item.is_dir():
            items.append(f"{relative_path}/")
        else:
            items.append(str(relative_path))
    
    return items


async def _cmd_edit(context: DSLContext, args: List[str]) -> str:
    """Edit a file."""
    if len(args) < 2:
        raise ValueError("Usage: edit <file_path> <content>")
    
    file_path = context.working_directory / args[0]
    content = " ".join(args[1:])
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    
    return f"Updated {args[0]}"


async def _cmd_mkdir(context: DSLContext, args: List[str]) -> str:
    """Create directory."""
    if not args:
        raise ValueError("Usage: mkdir <dir_path>")
    
    dir_path = context.working_directory / args[0]
    dir_path.mkdir(parents=True, exist_ok=True)
    
    return f"Created directory: {args[0]}"


async def _cmd_rm(context: DSLContext, args: List[str]) -> str:
    """Remove file or directory."""
    if not args:
        raise ValueError("Usage: rm <path>")
    
    target_path = context.working_directory / args[0]
    
    if not target_path.exists():
        raise ValueError(f"Path not found: {args[0]}")
    
    if target_path.is_dir():
        import shutil
        shutil.rmtree(target_path)
    else:
        target_path.unlink()
    
    return f"Removed: {args[0]}"


async def _cmd_sumd_scan(context: DSLContext, args: List[str]) -> Dict[str, Any]:
    """Scan project and generate SUMD."""
    from ..pipeline import RenderPipeline
    
    scan_path = context.working_directory
    profile = "rich"
    fix = False
    
    # Parse arguments
    for arg in args:
        if arg.startswith("--profile="):
            profile = arg.split("=", 1)[1]
        elif arg == "--fix":
            fix = True
        elif not arg.startswith("--"):
            scan_path = context.working_directory / arg
    
    pipeline = RenderPipeline(scan_path)
    content, sources = pipeline.run(profile=profile, return_sources=True)
    
    if fix:
        sumd_path = scan_path / "SUMD.md"
        sumd_path.write_text(content, encoding="utf-8")
        return {"action": "written", "file": str(sumd_path), "sources": sources}
    else:
        return {"action": "generated", "content": content, "sources": sources}


async def _cmd_sumd_map(context: DSLContext, args: List[str]) -> Dict[str, Any]:
    """Generate project map."""
    from ..extractor import generate_map_toon
    
    map_path = context.working_directory
    force = False
    
    # Parse arguments
    for arg in args:
        if arg == "--force":
            force = True
        elif not arg.startswith("--"):
            map_path = context.working_directory / arg
    
    content = generate_map_toon(map_path)
    
    output_file = map_path / "project" / "map.toon.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if force or not output_file.exists():
        output_file.write_text(content, encoding="utf-8")
        return {"action": "written", "file": str(output_file)}
    else:
        return {"action": "exists", "file": str(output_file), "content": content}


async def _cmd_sumd_validate(context: DSLContext, args: List[str]) -> Dict[str, Any]:
    """Validate SUMD document."""
    from ..parser import validate_sumd_file
    
    if not args:
        raise ValueError("Usage: sumd_validate <file_path>")
    
    file_path = context.working_directory / args[0]
    result = validate_sumd_file(file_path)
    
    return {
        "file": str(file_path),
        "valid": result["ok"],
        "markdown_issues": len(result.get("markdown", [])),
        "codeblock_issues": len(result.get("codeblocks", [])),
    }


async def _cmd_sumd_info(context: DSLContext, args: List[str]) -> Dict[str, Any]:
    """Show SUMD document info."""
    from ..parser import parse_file
    
    if not args:
        raise ValueError("Usage: sumd_info <file_path>")
    
    file_path = context.working_directory / args[0]
    doc = parse_file(file_path)
    
    return {
        "project_name": doc.project_name,
        "description": doc.description,
        "sections": len(doc.sections),
        "section_names": [s.name for s in doc.sections],
    }


async def _cmd_find(context: DSLContext, args: List[str]) -> List[str]:
    """Find files matching pattern."""
    if not args:
        raise ValueError("Usage: find <pattern> [path]")
    
    pattern = args[0]
    search_path = context.working_directory
    
    if len(args) > 1:
        search_path = context.working_directory / args[1]
    
    if not search_path.exists():
        raise ValueError(f"Path not found: {search_path}")
    
    files = []
    for file_path in search_path.rglob(pattern):
        if file_path.is_file():
            relative_path = file_path.relative_to(context.working_directory)
            files.append(str(relative_path))
    
    return sorted(files)


async def _cmd_grep(context: DSLContext, args: List[str]) -> List[Dict[str, Any]]:
    """Search for text in files."""
    if not args:
        raise ValueError("Usage: grep <pattern> [files]")
    
    pattern = args[0]
    file_patterns = args[1:] if len(args) > 1 else ["*"]
    
    results = []
    
    for file_pattern in file_patterns:
        for file_path in context.working_directory.glob(file_pattern):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.splitlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        if pattern in line:
                            results.append({
                                "file": str(file_path.relative_to(context.working_directory)),
                                "line": line_num,
                                "content": line.strip(),
                            })
                except Exception:
                    continue
    
    return results


async def _cmd_echo(context: DSLContext, args: List[str]) -> str:
    """Display message."""
    return " ".join(args)


async def _cmd_pwd(context: DSLContext, args: List[str]) -> str:
    """Print working directory."""
    return str(context.working_directory)


async def _cmd_cd(context: DSLContext, args: List[str]) -> str:
    """Change directory."""
    if not args:
        raise ValueError("Usage: cd <path>")
    
    new_path = context.working_directory / args[0]
    if not new_path.exists():
        raise ValueError(f"Directory not found: {args[0]}")
    
    if not new_path.is_dir():
        raise ValueError(f"Path is not a directory: {args[0]}")
    
    context.working_directory = new_path.resolve()
    return str(context.working_directory)


async def _cmd_help(context: DSLContext, args: List[str]) -> str:
    """Show help information."""
    registry = create_builtin_registry()
    
    if args:
        return registry.get_help(args[0])
    else:
        return registry.get_help()


async def _cmd_clear(context: DSLContext, args: List[str]) -> str:
    """Clear screen."""
    import os
    os.system("clear" if os.name != "nt" else "cls")
    return ""


async def _cmd_set(context: DSLContext, args: List[str]) -> str:
    """Set variable."""
    if len(args) < 2:
        raise ValueError("Usage: set <name> <value>")
    
    name = args[0]
    value = " ".join(args[1:])
    
    # Try to parse as JSON for complex values
    try:
        import json
        parsed_value = json.loads(value)
        context.set_variable(name, parsed_value)
    except (json.JSONDecodeError, ValueError):
        context.set_variable(name, value)
    
    return f"Set {name} = {value}"


async def _cmd_get(context: DSLContext, args: List[str]) -> str:
    """Get variable value."""
    if not args:
        raise ValueError("Usage: get <name>")
    
    value = context.get_variable(args[0])
    if value is None:
        return f"Variable '{args[0]}' not set"
    
    return f"{args[0]} = {value}"


async def _cmd_unset(context: DSLContext, args: List[str]) -> str:
    """Remove variable."""
    if not args:
        raise ValueError("Usage: unset <name>")
    
    if args[0] in context.variables:
        del context.variables[args[0]]
        return f"Removed variable '{args[0]}'"
    else:
        return f"Variable '{args[0]}' not set"


async def _cmd_vars(context: DSLContext, args: List[str]) -> List[str]:
    """List all variables."""
    variables = []
    for name, value in context.variables.items():
        variables.append(f"{name} = {value}")
    
    return sorted(variables)


async def _cmd_exists(context: DSLContext, args: List[str]) -> bool:
    """Check if file exists."""
    if not args:
        raise ValueError("Usage: exists <file_path>")
    
    file_path = context.working_directory / args[0]
    return file_path.exists()


async def _cmd_read_file(context: DSLContext, args: List[str]) -> str:
    """Read file contents."""
    if not args:
        raise ValueError("Usage: read_file <file_path>")
    
    file_path = context.working_directory / args[0]
    if not file_path.exists():
        raise ValueError(f"File not found: {args[0]}")
    
    return file_path.read_text(encoding="utf-8")
