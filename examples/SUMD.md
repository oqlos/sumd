# MyApp

Przykładowa aplikacja demonstrująca integrację SUMD z pakietami testql, doql i taskfile.

## Metadata

- **version**: 1.0.0
- **author**: Tom Sapletta
- **license**: Apache-2.0
- **language**: Python 3.10+
- **stack**: testql, doql, taskfile

## Intent

Aplikacja zarządzająca katalogiem produktów z interfejsem REST API, testami GUI oraz
automatycznym pipeline'em wdrożeniowym.

Trójwarstwowa architektura ekosystemu:

- **SUMD** opisuje projekt (opis, zamiar, architektura)
- **DOQL** wykonuje operacje na danych (zapytania, transformacje)
- **taskfile** zarządza automatyzacją (build, deploy, testy)
- **testql** weryfikuje interfejsy (API, GUI, endpointy)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MyApp                               │
│           REST API + CLI + Web UI                    │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼──────┐    ┌─────────▼───────┐
│  DOQL Layer  │    │  taskfile Layer  │
│  (dane)      │    │  (automatyzacja) │
└───────┬──────┘    └─────────┬───────┘
        │                     │
        └──────────┬──────────┘
                   │
          ┌────────▼────────┐
          │  testql Layer    │
          │  (weryfikacja)   │
          └─────────────────┘
```

## Interfaces

### REST API

- `GET /products` — lista produktów
- `POST /products` — dodaj produkt
- `GET /products/{id}` — szczegóły produktu
- `PUT /products/{id}` — aktualizuj produkt
- `DELETE /products/{id}` — usuń produkt

### CLI

```bash
myapp list-products
myapp add-product --name "Widget" --price 9.99
myapp export --format json --output products.json
```

### DOQL Queries

```doql
# Pobierz produkty droższe niż 10 PLN
SELECT * FROM products WHERE price > 10 ORDER BY name
```

### testql Scenarios

```testql
scenario: list_products
  GET /products
  status: 200
  body.items: array
  body.items[0].name: string
```

## Workflows

### Build & Test

```yaml
# Taskfile.yml — zarządzany przez pakiet taskfile
tasks:
  build:
    cmds:
      - pip install -e .
  test:
    cmds:
      - testql run testql-scenarios/
      - pytest tests/
  deploy:
    cmds:
      - taskfile deploy --env staging
```

### CI/CD Pipeline

Pipeline generowany automatycznie przez pakiet `taskfile`:

```bash
taskfile cigen --target github --output .github/workflows/ci.yml
taskfile cigen --target gitlab --output .gitlab-ci.yml
```

### testql Automation

```bash
# Uruchom wszystkie scenariusze testowe
testql run testql-scenarios/ --report json --output test-results.json

# Waliduj API względem OpenAPI spec
testql validate openapi.yaml --scenarios testql-scenarios/
```

## Configuration

```yaml
# myapp.config.yaml
database:
  url: sqlite:///myapp.db
  pool_size: 5

api:
  host: 0.0.0.0
  port: 8080

doql:
  dialect: sqlite
  auto_migrate: true

testql:
  base_url: http://localhost:8080
  timeout: 30

taskfile:
  default_env: local
  environments:
    - local
    - staging
    - prod
```

## Dependencies

### Python Packages

- `doql>=0.1.1` — Declarative Object Query Language
- `testql>=0.2.1` — Interface Query Language for testing
- `taskfile>=0.3.89` — Universal task runner
- `sumd>=0.1.7` — Project descriptor (ten dokument)
- `fastapi>=0.100.0` — REST API framework
- `uvicorn>=0.20.0` — ASGI server

### External Dependencies

- Python 3.10+
- Docker (opcjonalny, dla deploy)
- SQLite / PostgreSQL

## Deployment

### Local Development

```bash
taskfile run build
taskfile run dev
```

### Staging

```bash
taskfile deploy --env staging
testql run testql-scenarios/ --base-url https://staging.myapp.example.com
```

### Production

```bash
taskfile deploy --env prod
taskfile status --env prod
```
