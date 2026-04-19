# my-api

Sample REST API project for SUMD demo

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Code Analysis](#code-analysis)
- [API Stubs](#api-stubs)
- [Intent](#intent)

## Metadata

- **name**: `my-api`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **openapi_title**: My API v0.1.0
- **generated_from**: pyproject.toml, Taskfile.yml, openapi(5 ep), project/(1 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Interfaces

### CLI Entry Points

- `my-api`

### REST API (from `openapi.yaml`)

```yaml markpact:openapi path=openapi.yaml
openapi: "3.1.0"
info:
  title: My API
  version: "0.1.0"
  description: Sample REST API for SUMD demo

servers:
  - url: http://localhost:8000

paths:
  /health:
    get:
      summary: Health check
      operationId: health_check
      responses:
        "200":
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status: { type: string, example: ok }

  /items:
    get:
      summary: List all items
      operationId: list_items
      responses:
        "200":
          description: List of items
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Item"

    post:
      summary: Create an item
      operationId: create_item
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ItemCreate"
      responses:
        "201":
          description: Created item
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Item"

  /items/{item_id}:
    get:
      summary: Get item by ID
      operationId: get_item
      parameters:
        - name: item_id
          in: path
          required: true
          schema: { type: integer }
      responses:
        "200":
          description: Item details
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Item"
        "404":
          description: Item not found

    delete:
      summary: Delete an item
      operationId: delete_item
      parameters:
        - name: item_id
          in: path
          required: true
          schema: { type: integer }
      responses:
        "204":
          description: Deleted

components:
  schemas:
    Item:
      type: object
      properties:
        id:    { type: integer }
        name:  { type: string }
        value: { type: number }
      required: [id, name]

    ItemCreate:
      type: object
      properties:
        name:  { type: string }
        value: { type: number }
      required: [name]
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: "3"
tasks:
  install:
    desc: Install the project
    cmds:
      - pip install -e .
  run:
    desc: Start the development server
    cmds:
      - uvicorn my_api.main:app --reload
```

## Configuration

```yaml
project:
  name: my-api
  version: 0.1.0
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
fastapi
uvicorn
```

## Deployment

```bash markpact:run
pip install my-api

# development install
pip install -e .[dev]
```

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# sample-project | 0f 0L |  | 2026-04-19
# stats: 0 func | 0 cls | 0 mod | CC̄=1.0 | critical:0 | cycles:0
# alerts[5]: none
# hotspots[5]: none
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[0]:
D:
```

## API Stubs

*My API v0.1.0 — auto-generated stubs from `openapi.yaml`.*

```python markpact:openapi path=openapi.yaml
# default
def health_check() -> Response:  # Health check
    "GET /health"
def list_items() -> Response:  # List all items
    "GET /items"
def create_item() -> Response:  # Create an item
    "POST /items"
def get_item() -> Response:  # Get item by ID
    "GET /items/{item_id}"
def delete_item() -> Response:  # Delete an item
    "DELETE /items/{item_id}"

```

**Schemas**: `Item`, `ItemCreate`

## Intent

Sample REST API project for SUMD demo
