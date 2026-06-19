from pathlib import Path

import pytest

from appsec_kit.writer import write_configs

_WORKFLOW_PATH = Path(".github/workflows/security.yml")
_PRECOMMIT_PATH = Path(".pre-commit-config.yaml")


def _paths(results: list[tuple[str, str]]) -> set[str]:
    return {path for path, _ in results}


def _statuses(results: list[tuple[str, str]]) -> dict[str, str]:
    return dict(results)


# ---------------------------------------------------------------------------
# File creation
# ---------------------------------------------------------------------------


class TestFileCreation:
    def test_workflow_created_when_sast_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["sast"])
        assert (tmp_path / _WORKFLOW_PATH).exists()

    def test_workflow_created_when_deps_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["deps"])
        assert (tmp_path / _WORKFLOW_PATH).exists()

    def test_workflow_created_when_secrets_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["secrets"])
        assert (tmp_path / _WORKFLOW_PATH).exists()

    def test_workflow_not_created_when_only_precommit_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["precommit"])
        assert not (tmp_path / _WORKFLOW_PATH).exists()

    def test_precommit_created_when_precommit_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["precommit"])
        assert (tmp_path / _PRECOMMIT_PATH).exists()

    def test_precommit_not_created_when_only_ci_layers_selected(self, tmp_path):
        write_configs(tmp_path, "python", ["sast", "deps", "secrets"])
        assert not (tmp_path / _PRECOMMIT_PATH).exists()

    def test_github_workflows_directory_created_automatically(self, tmp_path):
        write_configs(tmp_path, "python", ["sast"])
        assert (tmp_path / ".github" / "workflows").is_dir()


# ---------------------------------------------------------------------------
# Status reporting
# ---------------------------------------------------------------------------


class TestStatusReporting:
    def test_status_is_created_for_new_workflow(self, tmp_path):
        results = write_configs(tmp_path, "python", ["sast"])
        assert _statuses(results)[".github/workflows/security.yml"] == "created"

    def test_status_is_updated_for_existing_workflow(self, tmp_path):
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / _WORKFLOW_PATH).write_text("old content")
        results = write_configs(tmp_path, "python", ["sast"])
        assert _statuses(results)[".github/workflows/security.yml"] == "updated"

    def test_status_is_created_for_new_precommit(self, tmp_path):
        results = write_configs(tmp_path, "python", ["precommit"])
        assert _statuses(results)[".pre-commit-config.yaml"] == "created"

    def test_status_is_updated_for_existing_precommit(self, tmp_path):
        (tmp_path / _PRECOMMIT_PATH).write_text("old content")
        results = write_configs(tmp_path, "python", ["precommit"])
        assert _statuses(results)[".pre-commit-config.yaml"] == "updated"


# ---------------------------------------------------------------------------
# pyproject.toml bandit config (Python only)
# ---------------------------------------------------------------------------


class TestBanditConfig:
    def test_appends_bandit_section_to_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        write_configs(tmp_path, "python", ["sast", "precommit"])
        assert "[tool.bandit]" in (tmp_path / "pyproject.toml").read_text()

    def test_pyproject_reported_as_updated(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        results = write_configs(tmp_path, "python", ["sast", "precommit"])
        assert "pyproject.toml" in _paths(results)
        assert _statuses(results)["pyproject.toml"] == "updated"

    def test_does_not_duplicate_bandit_section_if_already_present(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n[tool.bandit]\nskips = []\n")
        write_configs(tmp_path, "python", ["sast", "precommit"])
        content = (tmp_path / "pyproject.toml").read_text()
        assert content.count("[tool.bandit]") == 1

    def test_skips_bandit_config_when_no_pyproject(self, tmp_path):
        results = write_configs(tmp_path, "python", ["sast", "precommit"])
        assert "pyproject.toml" not in _paths(results)

    def test_skips_bandit_config_for_node_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        results = write_configs(tmp_path, "node", ["sast", "precommit"])
        assert "pyproject.toml" not in _paths(results)

    def test_skips_bandit_config_when_sast_not_selected(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        results = write_configs(tmp_path, "python", ["deps", "precommit"])
        assert "pyproject.toml" not in _paths(results)


# ---------------------------------------------------------------------------
# Workflow content per language
# ---------------------------------------------------------------------------


class TestWorkflowContent:
    def test_python_workflow_contains_bandit(self, tmp_path):
        write_configs(tmp_path, "python", ["sast"])
        content = (tmp_path / _WORKFLOW_PATH).read_text()
        assert "bandit" in content

    def test_node_workflow_contains_semgrep(self, tmp_path):
        write_configs(tmp_path, "node", ["sast"])
        content = (tmp_path / _WORKFLOW_PATH).read_text()
        assert "semgrep" in content.lower()

    def test_node_workflow_contains_npm_audit(self, tmp_path):
        write_configs(tmp_path, "node", ["deps"])
        content = (tmp_path / _WORKFLOW_PATH).read_text()
        assert "npm audit" in content

    def test_all_layers_python_produces_all_files(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        results = write_configs(tmp_path, "python", ["sast", "deps", "secrets", "precommit"])
        paths = _paths(results)
        assert ".github/workflows/security.yml" in paths
        assert ".pre-commit-config.yaml" in paths
        assert "pyproject.toml" in paths

    def test_all_layers_node_produces_workflow_and_precommit(self, tmp_path):
        results = write_configs(tmp_path, "node", ["sast", "deps", "secrets", "precommit"])
        paths = _paths(results)
        assert ".github/workflows/security.yml" in paths
        assert ".pre-commit-config.yaml" in paths
