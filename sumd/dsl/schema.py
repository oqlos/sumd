"""DSL Schema - Pydantic models for DSL data validation and project structure."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, ConfigDict


class DSLDataType(str, Enum):
    """Supported data types in DSL."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    DATETIME = "datetime"


class DSLCommandType(str, Enum):
    """Supported command types in DSL."""
    FILE = "file"
    SUMD = "sumd"
    SEARCH = "search"
    UTILITY = "utility"
    VARIABLE = "variable"
    SCHEMA = "schema"
    NLP = "nlp"


class DSLActionType(str, Enum):
    """Supported action types in DSL."""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    UPDATE = "update"
    LIST = "list"
    VALIDATE = "validate"
    ANALYZE = "analyze"
    PROCESS = "process"


class DSLParameter(BaseModel):
    """DSL parameter definition."""
    name: str = Field(..., description="Parameter name")
    data_type: DSLDataType = Field(..., description="Parameter data type")
    required: bool = Field(True, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value")
    description: Optional[str] = Field(None, description="Parameter description")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class DSLCommandSchema(BaseModel):
    """DSL command schema definition."""
    name: str = Field(..., description="Command name")
    command_type: DSLCommandType = Field(..., description="Command type")
    action_type: DSLActionType = Field(..., description="Action type")
    description: str = Field(..., description="Command description")
    parameters: List[DSLParameter] = Field(default_factory=list, description="Command parameters")
    returns: DSLDataType = Field(DSLDataType.STRING, description="Return data type")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    aliases: List[str] = Field(default_factory=list, description="Command aliases")


class DSLProjectSchema(BaseModel):
    """DSL project schema definition."""
    name: str = Field(..., description="Project name")
    version: str = Field(..., description="Schema version")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    
    # Project structure
    root_path: Path = Field(..., description="Project root path")
    config_files: List[str] = Field(default_factory=list, description="Configuration files")
    source_dirs: List[str] = Field(default_factory=list, description="Source directories")
    ignore_patterns: List[str] = Field(default_factory=list, description="Ignore patterns")
    
    # DSL configuration
    commands: List[DSLCommandSchema] = Field(default_factory=list, description="Available commands")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Global variables")
    functions: Dict[str, str] = Field(default_factory=dict, description="Custom function definitions")
    
    # NLP configuration
    nlp_enabled: bool = Field(True, description="Enable NLP features")
    nlp_models: List[str] = Field(default_factory=list, description="Available NLP models")
    nlp_intents: Dict[str, str] = Field(default_factory=dict, description="NLP intent mappings")


class DSLExpression(BaseModel):
    """DSL expression model."""
    type: str = Field(..., description="Expression type")
    value: Any = Field(..., description="Expression value")
    children: List["DSLExpression"] = Field(default_factory=list, description="Child expressions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Expression metadata")
    
    model_config = {"from_attributes": True}


class DSLStatement(BaseModel):
    """DSL statement model."""
    expression: DSLExpression = Field(..., description="Statement expression")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    result: Optional[Any] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Execution error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")


class DSLScript(BaseModel):
    """DSL script model."""
    name: str = Field(..., description="Script name")
    description: Optional[str] = Field(None, description="Script description")
    statements: List[DSLStatement] = Field(default_factory=list, description="Script statements")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Script variables")
    imports: List[str] = Field(default_factory=list, description="Import statements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Script metadata")
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")


class NLPIntent(BaseModel):
    """NLP intent model."""
    name: str = Field(..., description="Intent name")
    description: str = Field(..., description="Intent description")
    examples: List[str] = Field(..., description="Example phrases")
    entities: Dict[str, str] = Field(default_factory=dict, description="Expected entities")
    dsl_mapping: str = Field(..., description="DSL command mapping")


class NLPEntity(BaseModel):
    """NLP entity model."""
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type")
    values: List[str] = Field(..., description="Possible values")
    patterns: List[str] = Field(default_factory=list, description="Recognition patterns")


class NLPModel(BaseModel):
    """NLP model configuration."""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type")
    version: str = Field(..., description="Model version")
    intents: List[NLPIntent] = Field(default_factory=list, description="Supported intents")
    entities: List[NLPEntity] = Field(default_factory=list, description="Supported entities")
    confidence_threshold: float = Field(0.7, description="Confidence threshold")


class DSLContext(BaseModel):
    """DSL execution context model."""
    variables: Dict[str, Any] = Field(default_factory=dict, description="Context variables")
    functions: Dict[str, Any] = Field(default_factory=dict, description="Available functions")
    working_directory: Path = Field(..., description="Working directory")
    project_schema: Optional[DSLProjectSchema] = Field(None, description="Project schema")
    nlp_model: Optional[NLPModel] = Field(None, description="NLP model")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    
    model_config = {"arbitrary_types_allowed": True}


class DSLCommandResult(BaseModel):
    """DSL command execution result."""
    success: bool = Field(..., description="Execution success")
    result: Optional[Any] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    execution_time: float = Field(..., description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")


# Predefined command schemas
SUMD_COMMAND_SCHEMAS = [
    DSLCommandSchema(
        name="scan",
        command_type=DSLCommandType.SUMD,
        action_type=DSLActionType.ANALYZE,
        description="Scan project and generate SUMD documentation",
        parameters=[
            DSLParameter(name="path", data_type=DSLDataType.PATH, required=False, default="."),
            DSLParameter(name="profile", data_type=DSLDataType.STRING, required=False, default="rich"),
            DSLParameter(name="fix", data_type=DSLDataType.BOOLEAN, required=False, default=True),
        ],
        returns=DSLDataType.DICT,
        examples=["scan()", "scan('/path/to/project')", "scan(profile='minimal')"],
    ),
    DSLCommandSchema(
        name="validate",
        command_type=DSLCommandType.SUMD,
        action_type=DSLActionType.VALIDATE,
        description="Validate SUMD document",
        parameters=[
            DSLParameter(name="file", data_type=DSLDataType.PATH, required=True),
        ],
        returns=DSLDataType.DICT,
        examples=["validate('SUMD.md')", "validate('/path/to/SUMD.md')"],
    ),
    DSLCommandSchema(
        name="info",
        command_type=DSLCommandType.SUMD,
        action_type=DSLActionType.READ,
        description="Get SUMD document information",
        parameters=[
            DSLParameter(name="file", data_type=DSLDataType.PATH, required=True),
        ],
        returns=DSLDataType.DICT,
        examples=["info('SUMD.md')", "info('/path/to/SUMD.md')"],
    ),
]

FILE_COMMAND_SCHEMAS = [
    DSLCommandSchema(
        name="cat",
        command_type=DSLCommandType.FILE,
        action_type=DSLActionType.READ,
        description="Display file contents",
        parameters=[
            DSLParameter(name="file", data_type=DSLDataType.PATH, required=True),
        ],
        returns=DSLDataType.STRING,
        examples=["cat('README.md')", "cat('/path/to/file.txt')"],
        aliases=["type", "show"],
    ),
    DSLCommandSchema(
        name="ls",
        command_type=DSLCommandType.FILE,
        action_type=DSLActionType.LIST,
        description="List directory contents",
        parameters=[
            DSLParameter(name="path", data_type=DSLDataType.PATH, required=False, default="."),
            DSLParameter(name="pattern", data_type=DSLDataType.STRING, required=False, default="*"),
        ],
        returns=DSLDataType.LIST,
        examples=["ls()", "ls('src')", "ls(pattern='*.py')"],
        aliases=["dir", "list"],
    ),
    DSLCommandSchema(
        name="edit",
        command_type=DSLCommandType.FILE,
        action_type=DSLActionType.UPDATE,
        description="Edit file contents",
        parameters=[
            DSLParameter(name="file", data_type=DSLDataType.PATH, required=True),
            DSLParameter(name="content", data_type=DSLDataType.STRING, required=True),
        ],
        returns=DSLDataType.BOOLEAN,
        examples=["edit('file.txt', 'new content')"],
        aliases=["modify", "update"],
    ),
]

NLP_COMMAND_SCHEMAS = [
    DSLCommandSchema(
        name="ask",
        command_type=DSLCommandType.NLP,
        action_type=DSLActionType.PROCESS,
        description="Ask natural language question about project",
        parameters=[
            DSLParameter(name="question", data_type=DSLDataType.STRING, required=True),
            DSLParameter(name="context", data_type=DSLDataType.STRING, required=False),
        ],
        returns=DSLDataType.STRING,
        examples=["ask('What are the main dependencies?')", "ask('How to run tests?')"],
    ),
    DSLCommandSchema(
        name="summarize",
        command_type=DSLCommandType.NLP,
        action_type=DSLActionType.PROCESS,
        description="Generate summary of project or file",
        parameters=[
            DSLParameter(name="target", data_type=DSLDataType.STRING, required=False, default="project"),
            DSLParameter(name="length", data_type=DSLDataType.STRING, required=False, default="medium"),
        ],
        returns=DSLDataType.STRING,
        examples=["summarize()", "summarize('src/main.py')", "summarize(length='short')"],
    ),
    DSLCommandSchema(
        name="analyze_sentiment",
        command_type=DSLCommandType.NLP,
        action_type=DSLActionType.ANALYZE,
        description="Analyze sentiment of text",
        parameters=[
            DSLParameter(name="text", data_type=DSLDataType.STRING, required=True),
        ],
        returns=DSLDataType.DICT,
        examples=["analyze_sentiment('This is great code')"],
    ),
]

SCHEMA_COMMAND_SCHEMAS = [
    DSLCommandSchema(
        name="schema_info",
        command_type=DSLCommandType.SCHEMA,
        action_type=DSLActionType.READ,
        description="Get schema information",
        parameters=[],
        returns=DSLDataType.DICT,
        examples=["schema_info()"],
    ),
    DSLCommandSchema(
        name="list_commands",
        command_type=DSLCommandType.SCHEMA,
        action_type=DSLActionType.LIST,
        description="List available commands",
        parameters=[
            DSLParameter(name="type", data_type=DSLDataType.STRING, required=False),
        ],
        returns=DSLDataType.LIST,
        examples=["list_commands()", "list_commands(type='file')"],
    ),
    DSLCommandSchema(
        name="command_help",
        command_type=DSLCommandType.SCHEMA,
        action_type=DSLActionType.READ,
        description="Get command help",
        parameters=[
            DSLParameter(name="command", data_type=DSLDataType.STRING, required=True),
        ],
        returns=DSLDataType.DICT,
        examples=["command_help('scan')", "command_help('ls')"],
    ),
]

# Default project schema
DEFAULT_PROJECT_SCHEMA = DSLProjectSchema(
    name="SUMD Project",
    version="1.0.0",
    description="Default SUMD DSL project schema",
    root_path=Path("."),
    config_files=["pyproject.toml", "package.json", "Cargo.toml"],
    source_dirs=["src", "lib", "app"],
    ignore_patterns=["*.pyc", "__pycache__", ".git"],
    commands=SUMD_COMMAND_SCHEMAS + FILE_COMMAND_SCHEMAS + NLP_COMMAND_SCHEMAS + SCHEMA_COMMAND_SCHEMAS,
    variables={"project_name": "", "version": "1.0.0"},
    nlp_enabled=True,
    nlp_models=["default"],
)
