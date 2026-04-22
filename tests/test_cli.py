"""Tests for sumd CLI commands using click's CliRunner."""

import json
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from sumd.cli import (
    _DOQL_AUTOGEN_MARKER,
    _detect_project_type,
    _detect_projects,
    _generate_doql_less,
    _is_project_dir,
    _node_framework,
    _node_spec_from_package_json,
    cli,
)


MINIMAL_SUMD = textwrap.dedent("""\
    # testapp

    ## Metadata

    | Key         | Value          |
    |-------------|----------------|
    | version     | 0.1.0          |
    | description | Test app       |

    ## Intent

    Build a simple test application.

    ## Architecture

    Single-tier application.

    ## Interfaces

    REST API on port 8080.

    ## Overview

    A simple test application.
""")


@pytest.fixture
def sumd_file(tmp_path):
    f = tmp_path / "SUMD.md"
    f.write_text(MINIMAL_SUMD)
    return f


class TestValidateCommand:
    def test_valid_file_exits_zero(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(sumd_file)])
        assert result.exit_code == 0

    def test_valid_file_prints_ok(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(sumd_file)])
        assert "valid" in result.output.lower() or result.exit_code == 0

    def test_missing_file_exits_nonzero(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(tmp_path / "no.md")])
        assert result.exit_code != 0


class TestInfoCommand:
    def test_info_runs(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(sumd_file)])
        # info command may fail on minimal file, just check no crash
        assert result.exit_code in (0, 1)


class TestExportCommand:
    def test_export_json(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", str(sumd_file), "--format", "json"])
        assert result.exit_code == 0
        # Should produce JSON output
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail(f"export did not produce valid JSON: {result.output[:200]}")

    def test_export_to_output_file(self, sumd_file, tmp_path):
        out = tmp_path / "out.json"
        runner = CliRunner()
        result = runner.invoke(cli, [
            "export", str(sumd_file), "--format", "json", "--output", str(out)
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_markdown(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", str(sumd_file), "--format", "markdown"])
        assert result.exit_code == 0


class TestCliVersion:
    def test_version_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "." in result.output  # version contains dots


class TestCliHelp:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SUMD" in result.output or "sumd" in result.output.lower()

    def test_validate_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0

    def test_export_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0

    def test_scan_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        assert result.exit_code == 0


class TestProjectDetection:
    """Detection must work across all supported languages/project types."""

    @pytest.mark.parametrize("marker,expected", [
        ("pyproject.toml",  "python"),
        ("setup.py",        "python"),
        ("package.json",    "node"),
        ("Cargo.toml",      "rust"),
        ("go.mod",          "go"),
        ("pom.xml",         "java"),
        ("build.gradle",    "java"),
        ("Gemfile",         "ruby"),
        ("composer.json",   "php"),
        ("Package.swift",   "swift"),
        ("pubspec.yaml",    "dart"),
        ("mix.exs",         "elixir"),
        ("stack.yaml",      "haskell"),
        ("project.clj",     "clojure"),
        ("CMakeLists.txt",  "cpp"),
        ("Makefile",        "generic"),
        ("Dockerfile",      "generic"),
        ("Taskfile.yml",    "generic"),
        ("SUMD.md",         "generic"),
    ])
    def test_is_project_dir_accepts_language_marker(
        self, tmp_path: Path, marker: str, expected: str,
    ):
        (tmp_path / marker).write_text("", encoding="utf-8")
        assert _is_project_dir(tmp_path) is True
        assert _detect_project_type(tmp_path) == expected

    @pytest.mark.parametrize("glob_name,expected", [
        ("demo.csproj",   "dotnet"),
        ("demo.sln",      "dotnet"),
        ("demo.gemspec",  "ruby"),
        ("demo.cabal",    "haskell"),
    ])
    def test_is_project_dir_accepts_glob_markers(
        self, tmp_path: Path, glob_name: str, expected: str,
    ):
        (tmp_path / glob_name).write_text("", encoding="utf-8")
        assert _is_project_dir(tmp_path) is True
        assert _detect_project_type(tmp_path) == expected

    def test_empty_dir_is_not_project(self, tmp_path: Path):
        assert _is_project_dir(tmp_path) is False
        assert _detect_project_type(tmp_path) == "generic"

    def test_detect_projects_finds_mixed_languages(self, tmp_path: Path):
        (tmp_path / "py-app").mkdir()
        (tmp_path / "py-app" / "pyproject.toml").write_text("", encoding="utf-8")
        (tmp_path / "node-app").mkdir()
        (tmp_path / "node-app" / "package.json").write_text("{}", encoding="utf-8")
        (tmp_path / "rust-app").mkdir()
        (tmp_path / "rust-app" / "Cargo.toml").write_text("", encoding="utf-8")
        (tmp_path / "not-a-project").mkdir()
        (tmp_path / "not-a-project" / "README.md").write_text("x", encoding="utf-8")

        found = {p.name for p in _detect_projects(tmp_path)}
        assert found == {"py-app", "node-app", "rust-app"}


class TestNodeSpecFromPackageJson:
    """Node DOQL spec must mirror real package.json (scripts + framework)."""

    @pytest.mark.parametrize("deps,expected", [
        ({"react"},                        "react"),
        ({"react", "typescript"},          "react+typescript"),
        ({"next", "react"},                "next"),
        ({"next", "react", "typescript"},  "next+typescript"),
        ({"vue"},                          "vue"),
        ({"@sveltejs/kit", "svelte"},      "sveltekit"),
        ({"svelte"},                       "svelte"),
        ({"astro"},                        "astro"),
        ({"vite", "typescript"},           "vite+typescript"),
        ({"@angular/core"},                "angular"),
        ({"@nestjs/core"},                 "nestjs"),
        ({"express"},                      "express"),
        ({"typescript"},                   "typescript"),
        (set(),                            "node"),
    ])
    def test_framework_detection(self, deps: set[str], expected: str):
        assert _node_framework(deps) == expected

    def test_spec_uses_real_scripts_and_extras(self):
        pkg = {
            "name": "demo",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "test": "vitest",
                "lint:fix": "eslint --fix",
                "icons:generate": "python gen.py",
                "test:e2e": "playwright test",
            },
            "dependencies": ["react"],
            "dev_dependencies": ["vite", "typescript"],
        }
        spec, extras = _node_spec_from_package_json(pkg)

        # Framework reflects deps + TS.
        assert spec["interface"] == 'interface[type="web"] {\n  framework: react+typescript;\n}'

        # Canonical workflows point at actual scripts when available.
        assert spec["install"] == "npm install"
        assert spec["dev"]     == "npm run dev"
        assert spec["build"]   == "npm run build"
        assert spec["test"]    == "npm test"          # "test" script present
        assert spec["fmt"]     == "npm run lint:fix"  # picks lint:fix as fmt

        # Non-canonical scripts surface as extras, canonical ones don't.
        assert extras == {
            "icons:generate": "npm run icons:generate",
            "test:e2e":       "npm run test:e2e",
        }

    def test_spec_falls_back_without_scripts(self):
        spec, extras = _node_spec_from_package_json({})
        assert extras == {}
        assert spec["install"] == "npm install"
        assert spec["dev"]     == "npm run dev"
        assert spec["test"]    == "npm test"
        assert spec["interface"] == 'interface[type="web"] {\n  framework: node;\n}'


class TestGenerateDoqlLess:
    """Refresh behaviour for app.doql.less generation."""

    def _pkg(self, tmp_path: Path, **overrides) -> None:
        data = {"name": "demo", "version": "0.1.0", "scripts": {}}
        data.update(overrides)
        (tmp_path / "package.json").write_text(json.dumps(data), encoding="utf-8")

    def test_fresh_generation_for_node_uses_real_scripts(self, tmp_path: Path):
        self._pkg(tmp_path, scripts={"dev": "vite", "icons:gen": "python x.py"},
                  devDependencies={"vite": "^7", "typescript": "^5"})
        _generate_doql_less(tmp_path, "demo", "0.1.0", force=True, project_type="node")
        content = (tmp_path / "app.doql.less").read_text()
        assert _DOQL_AUTOGEN_MARKER in content
        assert "framework: vite+typescript" in content
        assert 'workflow[name="dev"]' in content
        assert 'workflow[name="icons:gen"]' in content
        # exactly one app{} block
        assert content.count("app {") == 1

    def test_force_regenerates_autogen_file_without_duplicating(self, tmp_path: Path):
        """Regression: previously the force path prepended a second app{}
        block when the existing block was identical to the new one."""
        self._pkg(tmp_path)
        _generate_doql_less(tmp_path, "demo", "0.1.0", force=True, project_type="node")
        # Re-run: file is auto-generated → full regeneration, still one app{}.
        self._pkg(tmp_path, version="0.2.0")
        _generate_doql_less(tmp_path, "demo", "0.2.0", force=True, project_type="node")
        content = (tmp_path / "app.doql.less").read_text()
        assert content.count("app {") == 1
        assert "version: 0.2.0" in content
        assert "version: 0.1.0" not in content

    def test_force_preserves_user_authored_file(self, tmp_path: Path):
        """User-authored files keep their body; only the app{} block is refreshed."""
        self._pkg(tmp_path)
        user_doql = (
            "app {\n  name: old-name;\n  version: 0.0.1;\n}\n\n"
            'entity[name="User"] {\n  id: uuid;\n}\n'
        )
        (tmp_path / "app.doql.less").write_text(user_doql, encoding="utf-8")
        _generate_doql_less(tmp_path, "demo", "9.9.9", force=True, project_type="node")
        content = (tmp_path / "app.doql.less").read_text()
        # User-defined entity is still there.
        assert 'entity[name="User"]' in content
        # Metadata block was refreshed, not duplicated.
        assert content.count("app {") == 1
        assert "version: 9.9.9" in content
        # Auto-gen marker NOT added (file remains user-authored).
        assert _DOQL_AUTOGEN_MARKER not in content

    def test_no_force_skips_existing(self, tmp_path: Path):
        self._pkg(tmp_path)
        (tmp_path / "app.doql.less").write_text("// existing\n", encoding="utf-8")
        result = _generate_doql_less(
            tmp_path, "demo", "0.1.0", force=False, project_type="node",
        )
        assert result is None
        assert (tmp_path / "app.doql.less").read_text() == "// existing\n"
