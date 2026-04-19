# Makefile — SUMD documentation targets

.PHONY: docs docs-minimal docs-refactor docs-lint docs-map docs-scaffold docs-export

## Generate SUMD.md (rich profile — default)
docs:
	sumd scan . --fix --profile rich

## Generate SUMD.md (minimal — faster)
docs-minimal:
	sumd scan . --fix --profile minimal

## Generate SUMR.md (pre-refactoring analysis)
docs-refactor:
	sumr . --fix

## Validate all SUMD.md files
docs-lint:
	sumd lint --workspace . --json

## Generate project/map.toon.yaml
docs-map:
	sumd map . --force

## Scaffold testql scenarios from OpenAPI
docs-scaffold:
	sumd scaffold . --force

## Export SUMD.md to JSON
docs-export:
	sumd export SUMD.md --format json -o sumd.json
	sumd export SUMD.md --format yaml -o sumd.yaml

## Full documentation pipeline
docs-all: docs-map docs docs-lint
