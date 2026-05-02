"""DSL Engine for executing SUMD DSL expressions."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass

from .parser import DSLExpression, DSLExpressionType, parse_dsl
from ..cqrs.commands import CommandBus, Command
from ..cqrs.queries import QueryBus, Query
from .schema import (
    DSLProjectSchema,
    DSLContext as SchemaDSLContext,
    DEFAULT_PROJECT_SCHEMA,
)
from .schema_commands import SchemaCommandRegistry, SchemaBasedCommands


@dataclass
class DSLContext:
    """Execution context for DSL expressions."""
    variables: Dict[str, Any]
    functions: Dict[str, Callable]
    working_directory: Path
    metadata: Dict[str, Any]
    
    def __init__(self, working_directory: Path = None):
        self.variables = {}
        self.functions = {}
        self.working_directory = working_directory or Path.cwd()
        self.metadata = {}
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable in the context."""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable from the context."""
        return self.variables.get(name)
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function in the context."""
        self.functions[name] = func
    
    def get_function(self, name: str) -> Optional[Callable]:
        """Get a function from the context."""
        return self.functions.get(name)


class DSLEngine:
    """Engine for executing DSL expressions."""
    
    def __init__(self, 
                 command_bus: Optional[CommandBus] = None, 
                 query_bus: Optional[QueryBus] = None,
                 project_schema: Optional[DSLProjectSchema] = None):
        self.command_bus = command_bus
        self.query_bus = query_bus
        self.project_schema = project_schema or DEFAULT_PROJECT_SCHEMA
        self.built_in_functions = self._initialize_builtin_functions()
        
        # Initialize schema-based commands
        self.schema_registry = SchemaCommandRegistry(self.project_schema)
        self.schema_commands = SchemaBasedCommands(
            DSLContext(self.project_schema.root_path),
            self.schema_registry
        )
    
    async def execute(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute a DSL expression in the given context."""
        return await self._execute_expression(expression, context)
    
    async def execute_text(self, text: str, context: DSLContext) -> Any:
        """Parse and execute DSL text."""
        # Check if this is natural language input
        if self._is_natural_language(text):
            nlp_result = self.schema_registry.process_natural_language(text)
            if nlp_result.success:
                # Convert NLP result to DSL and execute
                dsl_command = nlp_result.result["dsl_command"]
                return await self.execute_text(dsl_command, context)
        
        expression = parse_dsl(text)
        return await self.execute(expression, context)
    
    def _is_natural_language(self, text: str) -> bool:
        """Check if input is natural language rather than DSL."""
        # Simple heuristic: if it contains spaces and no special DSL characters
        dsl_chars = ["=", "+", "*", "/", "-", "(", ")", "[", "]", "{", "}", "|", "&", "!", "<", ">"]
        has_dsl_chars = any(char in text for char in dsl_chars)
        has_spaces = " " in text.strip()
        
        return has_spaces and not has_dsl_chars and len(text.split()) > 2
    
    async def process_natural_language(self, text: str) -> Any:
        """Process natural language input."""
        return self.schema_registry.process_natural_language(text)
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions."""
        return self.schema_registry.get_suggestions(partial_input)
    
    async def _execute_expression(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute a single DSL expression."""
        if expression.type == DSLExpressionType.LITERAL:
            return expression.value
        
        elif expression.type == DSLExpressionType.IDENTIFIER:
            return context.get_variable(expression.value) or expression.value
        
        elif expression.type == DSLExpressionType.ASSIGNMENT:
            return await self._execute_assignment(expression, context)
        
        elif expression.type == DSLExpressionType.COMMAND:
            return await self._execute_command(expression, context)
        
        elif expression.type == DSLExpressionType.FUNCTION_CALL:
            return await self._execute_function_call(expression, context)
        
        elif expression.type == DSLExpressionType.PROPERTY_ACCESS:
            return await self._execute_property_access(expression, context)
        
        elif expression.type == DSLExpressionType.COMPARISON:
            return await self._execute_comparison(expression, context)
        
        elif expression.type == DSLExpressionType.LOGICAL:
            return await self._execute_logical(expression, context)
        
        elif expression.type == DSLExpressionType.ARITHMETIC:
            return await self._execute_arithmetic(expression, context)
        
        elif expression.type == DSLExpressionType.PIPELINE:
            return await self._execute_pipeline(expression, context)
        
        elif expression.type == DSLExpressionType.LIST:
            return await self._execute_list(expression, context)
        
        elif expression.type == DSLExpressionType.DICT:
            return await self._execute_dict(expression, context)
        
        elif expression.type == DSLExpressionType.BLOCK:
            return await self._execute_block(expression, context)
        
        else:
            raise ValueError(f"Unknown expression type: {expression.type}")
    
    async def _execute_assignment(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute assignment expression."""
        if len(expression.children) != 2:
            raise ValueError("Assignment requires exactly 2 children")
        
        left = expression.children[0]
        right = expression.children[1]
        
        if left.type != DSLExpressionType.IDENTIFIER:
            raise ValueError("Left side of assignment must be identifier")
        
        value = await self._execute_expression(right, context)
        context.set_variable(left.value, value)
        
        return value
    
    async def _execute_command(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute command expression."""
        command_name = expression.value
        args = []
        
        # Evaluate arguments
        for arg_expr in expression.children:
            arg_value = await self._execute_expression(arg_expr, context)
            args.append(arg_value)
        
        # Check if it's a schema-based command
        if self.schema_registry.get_command(command_name):
            # Convert positional args to named args based on schema
            command_schema = self.schema_registry.get_command(command_name)
            named_args = {}
            
            for i, arg_value in enumerate(args):
                if i < len(command_schema.parameters):
                    param_name = command_schema.parameters[i].name
                    named_args[param_name] = arg_value
            
            # Update schema commands context
            self.schema_commands.context = context
            return await self.schema_commands.execute_command(command_name, named_args)
        
        # Check if it's a built-in function
        if command_name in self.built_in_functions:
            func = self.built_in_functions[command_name]
            return await self._call_function(func, args, context)
        
        # Check if it's a context function
        if command_name in context.functions:
            func = context.functions[command_name]
            return await self._call_function(func, args, context)
        
        # Otherwise, treat as SUMD command
        if self.command_bus:
            return await self._execute_sumd_command(command_name, args, context)
        
        raise ValueError(f"Unknown command: {command_name}")
    
    async def _execute_function_call(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute function call expression."""
        function_name = expression.value
        args = []
        
        # Evaluate arguments
        for arg_expr in expression.children:
            arg_value = await self._execute_expression(arg_expr, context)
            args.append(arg_value)
        
        # Check if it's a schema-based command
        if self.schema_registry.get_command(function_name):
            # Convert positional args to named args based on schema
            command_schema = self.schema_registry.get_command(function_name)
            named_args = {}
            
            for i, arg_value in enumerate(args):
                if i < len(command_schema.parameters):
                    param_name = command_schema.parameters[i].name
                    named_args[param_name] = arg_value
            
            # Update schema commands context
            self.schema_commands.context = context
            return await self.schema_commands.execute_command(function_name, named_args)
        
        # Check built-in functions
        if function_name in self.built_in_functions:
            func = self.built_in_functions[function_name]
            return await self._call_function(func, args, context)
        
        # Check context functions
        if function_name in context.functions:
            func = context.functions[function_name]
            return await self._call_function(func, args, context)
        
        raise ValueError(f"Unknown function: {function_name}")
    
    async def _execute_property_access(self, expression: DSLExpression, context: DSLExpression) -> Any:
        """Execute property access expression."""
        object_name = expression.value
        property_name = expression.children[0].value
        
        # Get the object
        obj = context.get_variable(object_name)
        if obj is None:
            raise ValueError(f"Unknown object: {object_name}")
        
        # Access property
        if hasattr(obj, property_name):
            return getattr(obj, property_name)
        elif isinstance(obj, dict) and property_name in obj:
            return obj[property_name]
        else:
            raise ValueError(f"Object {object_name} has no property {property_name}")
    
    async def _execute_comparison(self, expression: DSLExpression, context: DSLContext) -> bool:
        """Execute comparison expression."""
        if len(expression.children) != 2:
            raise ValueError("Comparison requires exactly 2 children")
        
        left = await self._execute_expression(expression.children[0], context)
        right = await self._execute_expression(expression.children[1], context)
        
        operator = expression.value
        
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        elif operator == "contains":
            return str(right) in str(left)
        elif operator == "matches":
            import re
            return bool(re.search(str(right), str(left)))
        elif operator == "startswith":
            return str(left).startswith(str(right))
        elif operator == "endswith":
            return str(left).endswith(str(right))
        else:
            raise ValueError(f"Unknown comparison operator: {operator}")
    
    async def _execute_logical(self, expression: DSLExpression, context: DSLContext) -> bool:
        """Execute logical expression."""
        operator = expression.value
        
        if operator == "not":
            if len(expression.children) != 1:
                raise ValueError("not requires exactly 1 operand")
            operand = await self._execute_expression(expression.children[0], context)
            return not operand
        
        elif operator in ["and", "or"]:
            if len(expression.children) != 2:
                raise ValueError(f"{operator} requires exactly 2 operands")
            
            left = await self._execute_expression(expression.children[0], context)
            right = await self._execute_expression(expression.children[1], context)
            
            if operator == "and":
                return left and right
            elif operator == "or":
                return left or right
        
        else:
            raise ValueError(f"Unknown logical operator: {operator}")
    
    async def _execute_arithmetic(self, expression: DSLExpression, context: DSLContext) -> Union[int, float]:
        """Execute arithmetic expression."""
        operator = expression.value
        
        if operator == "-" and len(expression.children) == 1:
            # Unary minus
            operand = await self._execute_expression(expression.children[0], context)
            return -operand
        
        elif len(expression.children) == 2:
            left = await self._execute_expression(expression.children[0], context)
            right = await self._execute_expression(expression.children[1], context)
            
            if operator == "+":
                return left + right
            elif operator == "-":
                return left - right
            elif operator == "*":
                return left * right
            elif operator == "/":
                return left / right
            elif operator == "%":
                return left % right
            elif operator == "**":
                return left ** right
            else:
                raise ValueError(f"Unknown arithmetic operator: {operator}")
        
        else:
            raise ValueError(f"Arithmetic operator {operator} requires 1 or 2 operands")
    
    async def _execute_pipeline(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute pipeline expression."""
        result = None
        
        for i, child in enumerate(expression.children):
            if i == 0:
                # First stage: execute normally
                result = await self._execute_expression(child, context)
            else:
                # Subsequent stages: treat as function call with previous result
                if child.type == DSLExpressionType.IDENTIFIER:
                    # Treat identifier as function call
                    func_name = child.value
                    
                    # Check built-in functions
                    if func_name in self.built_in_functions:
                        func = self.built_in_functions[func_name]
                        result = await self._call_function(func, [result], context)
                    # Check context functions
                    elif func_name in context.functions:
                        func = context.functions[func_name]
                        result = await self._call_function(func, [result], context)
                    else:
                        # Not a function, just return the identifier
                        result = func_name
                else:
                    # Execute other expression types normally
                    result = await self._execute_expression(child, context)
            
            # Set the result as a special variable for the next stage
            context.set_variable("_", result)
        
        return result
    
    async def _execute_list(self, expression: DSLExpression, context: DSLContext) -> List[Any]:
        """Execute list expression."""
        items = []
        
        for item_expr in expression.children:
            item = await self._execute_expression(item_expr, context)
            items.append(item)
        
        return items
    
    async def _execute_dict(self, expression: DSLExpression, context: DSLContext) -> Dict[str, Any]:
        """Execute dictionary expression."""
        result = {}
        
        for key_expr, value_expr in expression.metadata.get("items", []):
            key = await self._execute_expression(key_expr, context)
            value = await self._execute_expression(value_expr, context)
            result[str(key)] = value
        
        return result
    
    async def _execute_block(self, expression: DSLExpression, context: DSLContext) -> Any:
        """Execute block expression."""
        result = None
        
        for child in expression.children:
            result = await self._execute_expression(child, context)
        
        return result
    
    async def _execute_sumd_command(self, command_name: str, args: List[Any], context: DSLContext) -> Any:
        """Execute SUMD command via command bus."""
        if not self.command_bus:
            raise ValueError("Command bus not configured")
        
        from ..cqrs.commands import (
            CreateSumdDocument,
            UpdateSumdDocument,
            AddSumdSection,
            RemoveSumdSection,
            ValidateSumdDocument,
            ScanProject,
            GenerateMap,
        )
        
        # Map command names to command classes
        command_map = {
            "create": CreateSumdDocument,
            "update": UpdateSumdDocument,
            "add_section": AddSumdSection,
            "remove_section": RemoveSumdSection,
            "validate": ValidateSumdDocument,
            "scan": ScanProject,
            "map": GenerateMap,
        }
        
        command_class = command_map.get(command_name)
        if not command_class:
            raise ValueError(f"Unknown SUMD command: {command_name}")
        
        # Create command
        if args:
            data = args[0] if isinstance(args[0], dict) else {}
        else:
            data = {}
        
        command = command_class(
            aggregate_id=context.working_directory.name,
            data=data,
        )
        
        # Execute command
        events = await self.command_bus.dispatch(command)
        
        return {
            "command": command_name,
            "events": len(events),
            "success": True,
        }
    
    async def _call_function(self, func: Callable, args: List[Any], context: DSLContext) -> Any:
        """Call a function with arguments."""
        if asyncio.iscoroutinefunction(func):
            return await func(context, args)
        else:
            return func(context, args)
    
    def _initialize_builtin_functions(self) -> Dict[str, Callable]:
        """Initialize built-in functions."""
        return {
            "print": self._builtin_print,
            "len": self._builtin_len,
            "str": self._builtin_str,
            "int": self._builtin_int,
            "float": self._builtin_float,
            "bool": self._builtin_bool,
            "type": self._builtin_type,
            "write_file": self._builtin_write_file,
            "list_files": self._builtin_list_files,
            "cwd": self._builtin_cwd,
            "cd": self._builtin_cd,
            "help": self._builtin_help,
        }
    
    # Built-in function implementations
    async def _builtin_print(self, context: DSLContext, args: List[Any]) -> None:
        """Print arguments to console."""
        print(*args)
    
    def _builtin_len(self, context: DSLContext, args: List[Any]) -> int:
        """Get length of object."""
        if not args:
            raise ValueError("len() requires an argument")
        return len(args[0])
    
    def _builtin_str(self, context: DSLContext, args: List[Any]) -> str:
        """Convert object to string."""
        if not args:
            # Use the last result from context (pipeline variable)
            obj = context.variables.get('_', '')
        else:
            obj = args[0]
        return str(obj)
    
    def _builtin_int(self, context: DSLContext, args: List[Any]) -> int:
        """Convert object to int."""
        if not args:
            raise ValueError("int() requires an argument")
        return int(args[0])
    
    def _builtin_float(self, context: DSLContext, args: List[Any]) -> float:
        """Convert object to float."""
        if not args:
            raise ValueError("float() requires an argument")
        return float(args[0])
    
    def _builtin_bool(self, context: DSLContext, args: List[Any]) -> bool:
        """Convert object to bool."""
        if not args:
            raise ValueError("bool() requires an argument")
        return bool(args[0])
    
    def _builtin_type(self, context: DSLContext, args: List[Any]) -> str:
        """Get type of object."""
        if not args:
            raise ValueError("type() requires an argument")
        return type(args[0]).__name__
    
    async def _builtin_write_file(self, context: DSLContext, path: str, content: str) -> None:
        """Write content to file."""
        full_path = context.working_directory / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
    
    def _builtin_list_files(self, context: DSLContext, pattern: str = "*") -> List[str]:
        """List files matching pattern."""
        return [str(p.relative_to(context.working_directory)) 
                for p in context.working_directory.glob(pattern) 
                if p.is_file()]
    
    def _builtin_cwd(self, context: DSLContext) -> str:
        """Get current working directory."""
        return str(context.working_directory)
    
    def _builtin_cd(self, context: DSLContext, path: str) -> None:
        """Change working directory."""
        new_path = context.working_directory / path
        if new_path.is_dir():
            context.working_directory = new_path.resolve()
        else:
            raise ValueError(f"Directory not found: {path}")
    
    def _builtin_help(self, context: DSLContext) -> str:
        """Show help information."""
        help_text = """
SUMD DSL Built-in Functions:
  print(args...)           - Print arguments to console
  len(obj)                - Get length of object
  str(obj)                - Convert to string
  int(obj)                - Convert to integer
  float(obj)              - Convert to float
  bool(obj)               - Convert to boolean
  type(obj)               - Get type name
  exists(path)            - Check if file/directory exists
  read_file(path)         - Read file contents
  write_file(path, content) - Write content to file
  list_files(pattern)     - List files matching pattern
  cwd()                   - Get current working directory
  cd(path)                - Change working directory
  help()                  - Show this help

SUMD Commands:
  scan(path)              - Scan project and generate SUMD
  map(path)               - Generate project map
  validate(path)          - Validate SUMD document
  create(data)            - Create SUMD document
  update(data)            - Update SUMD document
  add_section(data)       - Add section to document
  remove_section(name)    - Remove section from document

DSL Examples:
  scan(".") | validate(".")
  files = list_files("*.md")
  if exists("SUMD.md"): print("SUMD found")
        """
        return help_text.strip()
