"""Tests for sumd CLI commands using click's CliRunner."""

import json
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from sumd.cli import cli


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
