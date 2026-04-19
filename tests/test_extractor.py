"""Tests for sumd/extractor.py — key extraction functions using tmp_path."""

from __future__ import annotations



from sumd.extractor import (
    extract_pyproject,
    extract_taskfile,
    extract_pyqual,
    extract_python_modules,
    extract_readme_title,
    extract_env,
    extract_goal,
    extract_project_analysis,
    extract_requirements,
    extract_makefile,
)


# ── extract_pyproject ────────────────────────────────────────────────────────


class TestExtractPyproject:
    def test_missing_file_returns_empty(self, tmp_path):
        assert extract_pyproject(tmp_path) == {}

    def test_basic_fields(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "mylib"\nversion = "1.2.3"\ndescription = "A lib"\n'
        )
        result = extract_pyproject(tmp_path)
        assert result["name"] == "mylib"
        assert result["version"] == "1.2.3"
        assert result["description"] == "A lib"

    def test_dependencies_parsed(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "x"\nversion = "0.1"\ndependencies = ["click>=8", "pyyaml"]\n'
        )
        result = extract_pyproject(tmp_path)
        assert "click>=8" in result["dependencies"]
        assert "pyyaml" in result["dependencies"]

    def test_dev_dependencies_from_optional(self, tmp_path):
        toml = (
            '[project]\nname = "x"\nversion = "0.1"\n\n'
            '[project.optional-dependencies]\ndev = ["pytest>=7", "ruff"]\n'
        )
        (tmp_path / "pyproject.toml").write_text(toml)
        result = extract_pyproject(tmp_path)
        assert "pytest>=7" in result["dev_dependencies"]

    def test_fallback_name_is_dir_name(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.1"\n')
        result = extract_pyproject(tmp_path)
        assert result["name"] == tmp_path.name

    def test_corrupt_toml_returns_empty(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("not: valid: toml: {{{{")
        result = extract_pyproject(tmp_path)
        assert result == {}


# ── extract_taskfile ─────────────────────────────────────────────────────────


class TestExtractTaskfile:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_taskfile(tmp_path) == []

    def test_parses_tasks(self, tmp_path):
        (tmp_path / "Taskfile.yml").write_text(
            "version: '3'\ntasks:\n  test:\n    desc: Run tests\n    cmds:\n      - pytest\n"
        )
        tasks = extract_taskfile(tmp_path)
        assert len(tasks) == 1
        assert tasks[0]["name"] == "test"
        assert tasks[0]["desc"] == "Run tests"
        assert tasks[0]["cmd"] == "pytest"

    def test_task_without_desc(self, tmp_path):
        (tmp_path / "Taskfile.yml").write_text(
            "version: '3'\ntasks:\n  build:\n    cmds:\n      - make\n"
        )
        tasks = extract_taskfile(tmp_path)
        assert tasks[0]["desc"] == ""

    def test_multiple_tasks(self, tmp_path):
        yaml_text = (
            "version: '3'\ntasks:\n"
            "  lint:\n    desc: Lint\n    cmds:\n      - ruff .\n"
            "  format:\n    desc: Format\n    cmds:\n      - black .\n"
        )
        (tmp_path / "Taskfile.yml").write_text(yaml_text)
        tasks = extract_taskfile(tmp_path)
        names = [t["name"] for t in tasks]
        assert "lint" in names
        assert "format" in names


# ── extract_pyqual ────────────────────────────────────────────────────────────


class TestExtractPyqual:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_pyqual(tmp_path) == {}

    def test_parses_pipeline(self, tmp_path):
        yaml_text = (
            "pipeline:\n"
            "  name: my-pipeline\n"
            "  stages:\n"
            "    - name: analyze\n      tool: radon\n"
            "  metrics:\n"
            "    cc_max: 10\n"
            "  loop: {}\n"
        )
        (tmp_path / "pyqual.yaml").write_text(yaml_text)
        result = extract_pyqual(tmp_path)
        assert result["name"] == "my-pipeline"
        assert result["stages"][0]["name"] == "analyze"
        assert result["metrics"]["cc_max"] == 10

    def test_flat_format(self, tmp_path):
        """pyqual.yaml without a `pipeline:` wrapper should still parse."""
        yaml_text = "name: flat-pipeline\nstages: []\nmetrics: {}\nloop: {}\n"
        (tmp_path / "pyqual.yaml").write_text(yaml_text)
        result = extract_pyqual(tmp_path)
        assert result["name"] == "flat-pipeline"


# ── extract_python_modules ────────────────────────────────────────────────────


class TestExtractPythonModules:
    def test_missing_pkg_dir_returns_empty(self, tmp_path):
        assert extract_python_modules(tmp_path, "mypkg") == []

    def test_lists_modules(self, tmp_path):
        pkg = tmp_path / "mypkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "core.py").write_text("")
        (pkg / "utils.py").write_text("")
        modules = extract_python_modules(tmp_path, "mypkg")
        assert "core" in modules
        assert "utils" in modules
        assert "__init__" not in modules

    def test_excludes_dunder_files(self, tmp_path):
        pkg = tmp_path / "mypkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "__main__.py").write_text("")
        (pkg / "cli.py").write_text("")
        modules = extract_python_modules(tmp_path, "mypkg")
        assert modules == ["cli"]


# ── extract_readme_title ──────────────────────────────────────────────────────


class TestExtractReadmeTitle:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_readme_title(tmp_path) == ""

    def test_extracts_h1(self, tmp_path):
        (tmp_path / "README.md").write_text("# My Project\n\nSome content\n")
        assert extract_readme_title(tmp_path) == "My Project"

    def test_no_h1_returns_empty(self, tmp_path):
        (tmp_path / "README.md").write_text("## Not H1\n\nContent\n")
        assert extract_readme_title(tmp_path) == ""

    def test_first_h1_only(self, tmp_path):
        (tmp_path / "README.md").write_text("# First\n\n# Second\n")
        assert extract_readme_title(tmp_path) == "First"


# ── extract_env ───────────────────────────────────────────────────────────────


class TestExtractEnv:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_env(tmp_path) == []

    def test_parses_key_value(self, tmp_path):
        (tmp_path / ".env.example").write_text("API_KEY=\nDEBUG=false\n")
        result = extract_env(tmp_path)
        keys = [v["key"] for v in result]
        assert "API_KEY" in keys
        assert "DEBUG" in keys

    def test_captures_preceding_comment(self, tmp_path):
        (tmp_path / ".env.example").write_text("# Secret key\nSECRET=abc\n")
        result = extract_env(tmp_path)
        assert result[0]["comment"] == "Secret key"

    def test_captures_inline_comment(self, tmp_path):
        (tmp_path / ".env.example").write_text("PORT=8080  # HTTP port\n")
        result = extract_env(tmp_path)
        assert result[0]["default"] == "8080"
        assert result[0]["comment"] == "HTTP port"

    def test_empty_value_becomes_not_set(self, tmp_path):
        (tmp_path / ".env.example").write_text("TOKEN=\n")
        result = extract_env(tmp_path)
        assert result[0]["default"] == "*(not set)*"


# ── extract_goal ──────────────────────────────────────────────────────────────


class TestExtractGoal:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_goal(tmp_path) == {}

    def test_parses_project_and_versioning(self, tmp_path):
        yaml_text = (
            "project:\n  name: mypkg\n  type: [library]\n  description: Desc\n"
            "versioning:\n  strategy: semver\n  files: [VERSION]\n"
            "git:\n  commit:\n    strategy: squash\n    scope: angular\n"
            "  changelog:\n    template: keep-a-changelog\n"
            "strategies: {}\nquality: {}\n"
        )
        (tmp_path / "goal.yaml").write_text(yaml_text)
        result = extract_goal(tmp_path)
        assert result["name"] == "mypkg"
        assert result["versioning_strategy"] == "semver"
        assert result["commit_strategy"] == "squash"


# ── extract_project_analysis ──────────────────────────────────────────────────


class TestExtractProjectAnalysis:
    def test_missing_project_dir_returns_empty(self, tmp_path):
        assert extract_project_analysis(tmp_path) == []

    def test_loads_calls_toon_yaml(self, tmp_path):
        proj_dir = tmp_path / "project"
        proj_dir.mkdir()
        (proj_dir / "calls.toon.yaml").write_text("HUBS[0]:\n  mod.func\n")
        result = extract_project_analysis(tmp_path)
        assert len(result) == 1
        assert result[0]["file"] == "project/calls.toon.yaml"
        assert "HUBS" in result[0]["content"]

    def test_refactor_mode_loads_extra_files(self, tmp_path):
        proj_dir = tmp_path / "project"
        proj_dir.mkdir()
        (proj_dir / "calls.toon.yaml").write_text("calls")
        (proj_dir / "analysis.toon.yaml").write_text("analysis")
        (proj_dir / "duplication.toon.yaml").write_text("duplication")

        standard = extract_project_analysis(tmp_path, refactor=False)
        standard_files = [r["file"] for r in standard]
        assert "project/analysis.toon.yaml" not in standard_files

        refactor = extract_project_analysis(tmp_path, refactor=True)
        refactor_files = [r["file"] for r in refactor]
        assert "project/analysis.toon.yaml" in refactor_files
        assert "project/duplication.toon.yaml" in refactor_files

    def test_missing_files_skipped(self, tmp_path):
        (tmp_path / "project").mkdir()
        # no files written — should return empty list
        result = extract_project_analysis(tmp_path)
        assert result == []


# ── extract_requirements ──────────────────────────────────────────────────────


class TestExtractRequirements:
    def test_no_requirements_returns_empty(self, tmp_path):
        assert extract_requirements(tmp_path) == []

    def test_parses_requirements_txt(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests==2.28.0\nflask>=2.0\n")
        result = extract_requirements(tmp_path)
        assert len(result) == 1
        assert "requests==2.28.0" in result[0]["deps"]

    def test_ignores_comments_and_flags(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("# comment\n-r base.txt\nclick>=8\n")
        result = extract_requirements(tmp_path)
        assert result[0]["deps"] == ["click>=8"]


# ── extract_makefile ──────────────────────────────────────────────────────────


class TestExtractMakefile:
    def test_missing_returns_empty(self, tmp_path):
        assert extract_makefile(tmp_path) == []

    def test_parses_targets(self, tmp_path):
        makefile = (
            "## Run tests\ntest:\n\tpytest\n\n## Build project\nbuild:\n\tmake all\n"
        )
        (tmp_path / "Makefile").write_text(makefile)
        result = extract_makefile(tmp_path)
        names = [t["target"] for t in result]
        assert "test" in names
        assert "build" in names

    def test_comment_captured(self, tmp_path):
        (tmp_path / "Makefile").write_text("## Do the thing\ndo:\n\techo hi\n")
        result = extract_makefile(tmp_path)
        assert result[0]["desc"] == "Do the thing"
