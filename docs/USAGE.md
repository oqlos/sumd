# Dokumentacja SUMD — integracja z testql, doql, taskfile

## Przegląd ekosystemu

SUMD jest częścią trójwarstwowego ekosystemu narzędzi:

| Warstwa | Pakiet | Rola |
|---------|--------|------|
| Opis | `sumd` | Strukturalny opis projektu dla ludzi i LLM |
| Dane | `doql` | Deklaratywne zapytania i transformacje danych |
| Automatyzacja | `taskfile` | Task runner, deploy, CI/CD |
| Testy | `testql` | Testowanie interfejsów API, GUI, CLI |

## Instalacja

```bash
pip install sumd doql testql taskfile
```

## Szybki start

### 1. Utwórz `SUMD.md` dla swojego projektu

```bash
# Skopiuj przykładowy szablon
cp examples/SUMD.md SUMD.md
```

Plik `SUMD.md` powinien zawierać sekcje:
- `## Metadata` — wersja, autor, stos technologiczny
- `## Intent` — cel i zakres projektu
- `## Architecture` — diagram i opis architektury
- `## Interfaces` — API, CLI, DOQL queries, testql scenarios
- `## Workflows` — pipeline build/test/deploy (taskfile)
- `## Configuration` — konfiguracja środowisk
- `## Dependencies` — zależności Python i zewnętrzne
- `## Deployment` — instrukcje wdrożenia

### 2. Walidacja dokumentu

```bash
sumd validate SUMD.md
```

### 3. Eksport do formatów strukturalnych

```bash
# Do JSON (dla API, LLM context injection)
sumd export SUMD.md --format json --output sumd.json

# Do YAML (dla konfiguracji)
sumd export SUMD.md --format yaml --output sumd.yaml

# Do TOML
sumd export SUMD.md --format toml --output sumd.toml
```

### 4. Generowanie SUMD z formatu strukturalnego

```bash
sumd generate sumd.json --format json --output SUMD.md
sumd generate sumd.yaml --format yaml --output SUMD.md
```

---

## Integracja z `doql`

DOQL (Declarative Object Query Language) umożliwia opisanie operacji na danych bezpośrednio w dokumencie SUMD w sekcji `## Interfaces`.

### Przykład zapytań w SUMD

````markdown
## Interfaces

### DOQL Queries

```doql
# Lista aktywnych użytkowników
SELECT id, name, email FROM users WHERE active = true ORDER BY name

# Statystyki zamówień
SELECT COUNT(*), SUM(total) FROM orders WHERE created_at > '2026-01-01'
```
````

### Python API — parsowanie sekcji DOQL

```python
from sumd import parse_file

doc = parse_file("SUMD.md")

# Znajdź sekcję Interfaces
interfaces = next(
    (s for s in doc.sections if s.type.value == "interfaces"),
    None
)
if interfaces:
    print(interfaces.content)
```

---

## Integracja z `testql`

TestQL definiuje scenariusze testowe interfejsów. Scenariusze są dokumentowane w SUMD i uruchamiane przez CLI testql.

### Przykład scenariuszy w SUMD

````markdown
## Interfaces

### testql Scenarios

```testql
scenario: health_check
  GET /health
  status: 200
  body.status: "ok"

scenario: list_products
  GET /products
  status: 200
  body.items: array
```
````

### Uruchamianie testów

```bash
# Uruchom scenariusze opisane w SUMD
testql run testql-scenarios/

# Raport JSON
testql run testql-scenarios/ --report json --output test-results.json

# Walidacja względem OpenAPI spec
testql validate openapi.yaml --scenarios testql-scenarios/
```

### Przykładowy plik scenariusza (`testql-scenarios/products.testql.yaml`)

```yaml
scenario: list_products
  request:
    method: GET
    path: /products
  expect:
    status: 200
    body:
      items:
        type: array
```

---

## Integracja z `taskfile`

Pakiet `taskfile` zarządza automatyzacją: build, test, deploy, CI/CD. Workflows są dokumentowane w sekcji `## Workflows` w SUMD.

### Przykładowy `Taskfile.yml`

```yaml
version: "3"

vars:
  APP_NAME: myapp
  PYTHON: python3

tasks:
  build:
    desc: "Zainstaluj zależności"
    cmds:
      - pip install -e ".[dev]"

  test:
    desc: "Uruchom testy (testql + pytest)"
    cmds:
      - testql run testql-scenarios/
      - pytest tests/ -v

  validate-sumd:
    desc: "Waliduj dokumentację SUMD"
    cmds:
      - sumd validate SUMD.md

  export-docs:
    desc: "Eksportuj SUMD do JSON i YAML"
    cmds:
      - sumd export SUMD.md --format json --output sumd.json
      - sumd export SUMD.md --format yaml --output sumd.yaml

  deploy:
    desc: "Wdróż aplikację"
    cmds:
      - taskfile deploy --env {{.ENV | default "staging"}}
    vars:
      ENV: "{{.ENV}}"

  ci:
    desc: "Wygeneruj konfiguracje CI/CD"
    cmds:
      - taskfile cigen --target github --output .github/workflows/ci.yml
      - taskfile cigen --target gitlab --output .gitlab-ci.yml
```

### Python API taskfile

```python
from taskfile import TaskfileRunner, TaskfileConfig

runner = TaskfileRunner("Taskfile.yml")

# Uruchom zadanie
runner.run("build")
runner.run("test")

# Deploy do środowiska
runner.run("deploy", env={"ENV": "staging"})
```

---

## Pełny przykład projektu

Struktura plików dla projektu używającego całego ekosystemu:

```
myapp/
├── SUMD.md                    # Opis projektu (sumd)
├── sumd.json                  # Eksport do JSON
├── Taskfile.yml               # Automatyzacja (taskfile)
├── openapi.yaml               # Specyfikacja API
├── app.doql                   # Deklaracje danych (doql)
├── testql-scenarios/          # Scenariusze testowe (testql)
│   ├── health.testql.yaml
│   └── products.testql.yaml
├── myapp/
│   └── __init__.py
└── tests/
    └── test_myapp.py
```

### Przepływ pracy

```bash
# 1. Waliduj dokumentację
sumd validate SUMD.md

# 2. Uruchom testy
taskfile run test

# 3. Eksportuj docs
taskfile run export-docs

# 4. Wdróż
taskfile run deploy ENV=staging
```

---

## Generowanie przykładów programowo

```python
from sumd import parse_file
import json

# Parsuj SUMD.md
doc = parse_file("SUMD.md")

# Eksportuj do JSON
data = {
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

with open("sumd.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Wygenerowano sumd.json dla projektu: {doc.project_name}")
print(f"Liczba sekcji: {len(doc.sections)}")
for section in doc.sections:
    print(f"  - {section.name} ({section.type.value})")
```

---

## Pliki przykładowe

- [examples/SUMD.md](../examples/SUMD.md) — przykładowy dokument SUMD
- [examples/sumd.json](../examples/sumd.json) — przykładowy eksport JSON
