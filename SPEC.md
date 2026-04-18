# SUMD v1 Specification

## Overview

SUMD (Structured Unified Markdown Descriptor) is a semantic project descriptor format in Markdown that defines intent, structure, execution entry points, and mental model of a system for both humans and LLMs.

## Ecosystem Context

SUMD is part of a three-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│                     SUMD (opis)                              │
│              Structured Unified Markdown Descriptor          │
│         Project description, intent, architecture            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DOQL (wykonanie)                          │
│              Declarative Object Query Language               │
│              Data manipulation and execution                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Taskfile (runtime)                          │
│              Task runner and workflow execution              │
│              Automation and orchestration                   │
└─────────────────────────────────────────────────────────────┘
```

- **SUMD → opis (description)**: Defines what the system is and how it should work
- **DOQL → wykonanie (execution)**: Provides the language to manipulate and execute operations
- **Taskfile → runtime**: Manages the actual execution of workflows and tasks

SUMD documents can reference DOQL queries and Taskfile workflows to provide complete system documentation.

## Format Conversion

SUMD documents can be converted to and from multiple structured formats for interoperability:

### Supported Export Formats

- **Markdown** (`.md`): Native SUMD format
- **JSON** (`.json`): Structured data for API consumption
- **YAML** (`.yaml`): Human-readable configuration format
- **TOML** (`.toml`): Configuration file format

### CLI Commands

```bash
# Export SUMD to different formats
sumd export SUMD.md --format json --output sumd.json
sumd export SUMD.md --format yaml --output sumd.yaml
sumd export SUMD.md --format toml --output sumd.toml
sumd export SUMD.md --format markdown --output sumd.md

# Generate SUMD from structured format
sumd generate sumd.json --format json --output SUMD.md
sumd generate sumd.yaml --format yaml --output SUMD.md
sumd generate sumd.toml --format toml --output SUMD.md
```

### Conversion Schema

When exporting to structured formats, SUMD documents follow this schema:

```json
{
  "project_name": "string",
  "description": "string",
  "sections": [
    {
      "name": "string",
      "type": "string",
      "content": "string",
      "level": "number"
    }
  ]
}
```

## Format Structure

A SUMD document is a Markdown file with structured sections using specific headers and syntax patterns.

### File Naming Convention

- Default: `SUMD.md` or `sumd.md`
- Alternative: `PROJECT_SUMD.md`, `app.sumd.md`
- Extension: `.md` (Markdown)

### Document Structure

```markdown
# [Project Name]

[Project description]

## Section Name
[Content]
```

## Required Sections

### 1. Project Header

```markdown
# [Project Name]

[One-line description of the project]
```

**Rules:**
- Must be the first line (H1)
- Project name should be kebab-case or PascalCase
- Description should be concise (1-2 sentences)

### 2. Metadata Block (Optional but Recommended)

```markdown
## Metadata

- **Version**: [semantic version]
- **Status**: [alpha|beta|stable|deprecated]
- **Author**: [name or organization]
- **License**: [SPDX identifier]
```

### 3. Intent Section

```markdown
## Intent

[What the project aims to achieve, its purpose, and goals]
```

**Purpose:** Defines the "why" of the project for both humans and LLMs.

### 4. Architecture Section

```markdown
## Architecture

### System Overview
[High-level system description]

### Components
- **[Component Name]**: [Description]
- **[Component Name]**: [Description]

### Data Flow
[Description of how data moves through the system]
```

### 5. Interfaces Section

```markdown
## Interfaces

### API
- **Endpoint**: [HTTP method] [path]
  - **Description**: [What it does]
  - **Parameters**: [Request parameters]
  - **Response**: [Response format]

### CLI
- **Command**: `[command]`
  - **Description**: [What it does]
  - **Usage**: `[command] [options]`
  - **Examples**: [Example usage]
```

### 6. Workflows Section

```markdown
## Workflows

### [Workflow Name]
- **Trigger**: [manual|automatic|event]
- **Steps**:
  1. [Step description]
  2. [Step description]
- **Dependencies**: [Required tools/services]
```

## Optional Sections

### Configuration

```markdown
## Configuration

### Environment Variables
- **[VAR_NAME]**: [Description] (default: [value])

### Settings
- **[setting]**: [Description] (default: [value])
```

### Dependencies

```markdown
## Dependencies

### Runtime
- [Dependency] ([version])

### Development
- [Dependency] ([version])
```

### Deployment

```markdown
## Deployment

### Environments
- **[env]**: [Description]

### Requirements
- [Requirement 1]
- [Requirement 2]
```

## Syntax Rules

### Headers

- Use H1 (`#`) for project name only
- Use H2 (`##`) for main sections
- Use H3 (`###`) for subsections
- Use H4 (`####`) for nested items (rare)

### Lists

- Use bullet points (`-`) for unordered lists
- Use numbered lists (`1.`) for sequences
- Nested lists should use 2-space indentation

### Code Blocks

- Use fenced code blocks with language identifier
- For configuration examples, use appropriate language (yaml, json, etc.)

```yaml
key: value
```

### Emphasis

- Use **bold** for key terms and section headers within content
- Use `code` for technical terms, commands, and variable names
- Use *italics* for emphasis sparingly

### Links

- Use descriptive link text: `[text](url)`
- For internal references, use anchor links: `[Section](#section)`

## LLM Optimization

### Semantic Structure

- Use clear, descriptive section names
- Maintain consistent hierarchy
- Provide context before details

### Context Injection

- Include intent and architecture early
- Define mental model explicitly
- Use consistent terminology

### Examples

Always provide examples for:
- API endpoints
- CLI commands
- Configuration
- Workflows

## Example SUMD Document

```markdown
# doql

Declarative Object Query Language for structured data manipulation.

## Metadata

- **Version**: 1.0.0
- **Status**: stable
- **Author**: Tom Sapletta
- **License**: Apache-2.0

## Intent

doql provides a declarative language for querying and manipulating structured data sources. It aims to simplify data operations by abstracting implementation details behind a unified syntax.

## Architecture

### System Overview
doql consists of a parser, interpreter, and multiple backend adapters for different data sources.

### Components
- **Parser**: Converts doql syntax into AST
- **Interpreter**: Executes AST against data sources
- **Adapters**: Interface to specific data backends (SQL, API, files)

### Data Flow
1. Parse doql query into AST
2. Validate AST against schema
3. Execute via appropriate adapter
4. Return formatted results

## Interfaces

### API
- **Endpoint**: POST /api/v1/query
  - **Description**: Execute doql query
  - **Parameters**: `{ "query": "string", "source": "string" }`
  - **Response**: `{ "results": [...], "metadata": {...} }`

### CLI
- **Command**: `doql query [file]`
  - **Description**: Execute doql query from file
  - **Usage**: `doql query data.doql --format json`
  - **Examples**: `doql query users.doql --output results.json`

## Workflows

### Query Execution
- **Trigger**: manual
- **Steps**:
  1. Parse query file
  2. Connect to data source
  3. Execute query
  4. Format output
- **Dependencies**: Python 3.10+, required adapter

## Configuration

### Environment Variables
- **DOQL_SOURCE**: Default data source (default: sqlite://db.sqlite)
- **DOQL_FORMAT**: Default output format (default: json)

## Deployment

### Environments
- **Development**: Local execution with file-based sources
- **Production**: Server mode with persistent connections

### Requirements
- Python 3.10+
- Required database adapters
```

## Best Practices

1. **Be concise but complete**: Provide enough context without overwhelming detail
2. **Maintain consistency**: Use similar structure across sections
3. **Think in layers**: Start with high-level, drill down to specifics
4. **Include examples**: Show, don't just tell
5. **Keep it current**: Update as project evolves
6. **Use semantic naming**: Section names should be self-explanatory
7. **Optimize for AI**: Structure for LLM context injection

## Version History

- **v1.0** (2026-04-18): Initial specification
  - Defined core structure
  - Established required and optional sections
  - Documented syntax rules
- **v1.1** (2026-04-18): Format conversion support
  - Added multi-format export (markdown, json, yaml, toml)
  - Added generate command for creating SUMD from structured formats
  - Documented conversion schema and CLI commands
