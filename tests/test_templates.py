import pytest

from appsec_kit.templates.node_templates import (
    build_node_precommit_config,
    build_node_workflow,
)
from appsec_kit.templates.python_templates import (
    build_python_precommit_config,
    build_python_workflow,
)
from appsec_kit.versions import BANDIT, DETECT_SECRETS, GITLEAKS, PIP_AUDIT

_ALL_CI = ["sast", "deps", "secrets"]
_ALL_LAYERS = [*_ALL_CI, "precommit"]


# ---------------------------------------------------------------------------
# Python workflow
# ---------------------------------------------------------------------------


class TestPythonWorkflow:
    def test_has_workflow_level_read_permission(self):
        wf = build_python_workflow(_ALL_CI)
        assert "permissions:" in wf
        assert "contents: read" in wf

    def test_sast_job_present_when_selected(self):
        wf = build_python_workflow(["sast"])
        assert "bandit" in wf

    def test_sast_job_absent_when_not_selected(self):
        wf = build_python_workflow(["deps", "secrets"])
        assert "bandit" not in wf

    def test_sast_job_has_security_events_write(self):
        wf = build_python_workflow(["sast"])
        assert "security-events: write" in wf

    def test_sast_uses_medium_severity_threshold(self):
        wf = build_python_workflow(["sast"])
        assert "-ll" in wf

    def test_sast_outputs_sarif(self):
        wf = build_python_workflow(["sast"])
        assert "bandit.sarif" in wf

    def test_sast_uploads_sarif_to_github(self):
        wf = build_python_workflow(["sast"])
        assert "upload-sarif" in wf

    def test_sast_has_enforcement_step(self):
        wf = build_python_workflow(["sast"])
        assert "Fail if findings found" in wf
        assert "steps.bandit.outcome" in wf

    def test_deps_job_present_when_selected(self):
        wf = build_python_workflow(["deps"])
        assert "pip-audit" in wf

    def test_deps_job_absent_when_not_selected(self):
        wf = build_python_workflow(["sast"])
        assert "pip-audit" not in wf

    def test_secret_scan_job_present_when_selected(self):
        wf = build_python_workflow(["secrets"])
        assert "gitleaks" in wf.lower()

    def test_secret_scan_has_security_events_write(self):
        wf = build_python_workflow(["secrets"])
        assert "security-events: write" in wf

    def test_all_jobs_combined(self):
        wf = build_python_workflow(_ALL_CI)
        assert "bandit" in wf
        assert "pip-audit" in wf
        assert "gitleaks" in wf.lower()

    def test_empty_layers_produces_header_only(self):
        wf = build_python_workflow([])
        assert "name: Security Scan" in wf
        assert "bandit" not in wf
        assert "pip-audit" not in wf


# ---------------------------------------------------------------------------
# Python pre-commit
# ---------------------------------------------------------------------------


class TestPythonPrecommit:
    def test_bandit_hook_uses_version_constant(self):
        pc = build_python_precommit_config(_ALL_LAYERS)
        assert f"rev: {BANDIT}" in pc

    def test_detect_secrets_hook_uses_version_constant(self):
        pc = build_python_precommit_config(_ALL_LAYERS)
        assert f"rev: {DETECT_SECRETS}" in pc

    def test_pip_audit_hook_uses_version_constant(self):
        pc = build_python_precommit_config(_ALL_LAYERS)
        assert f"rev: {PIP_AUDIT}" in pc

    def test_sast_hook_included_when_selected(self):
        pc = build_python_precommit_config(["sast", "precommit"])
        assert "bandit" in pc

    def test_sast_hook_excluded_when_not_selected(self):
        pc = build_python_precommit_config(["secrets", "precommit"])
        assert "bandit" not in pc

    def test_secrets_hook_included_when_selected(self):
        pc = build_python_precommit_config(["secrets", "precommit"])
        assert "detect-secrets" in pc

    def test_deps_hook_included_when_selected(self):
        pc = build_python_precommit_config(["deps", "precommit"])
        assert "pip-audit" in pc

    def test_empty_repos_when_no_security_layers(self):
        pc = build_python_precommit_config(["precommit"])
        assert pc == "repos: []\n"


# ---------------------------------------------------------------------------
# Node workflow
# ---------------------------------------------------------------------------


class TestNodeWorkflow:
    def test_has_workflow_level_read_permission(self):
        wf = build_node_workflow(_ALL_CI)
        assert "permissions:" in wf
        assert "contents: read" in wf

    def test_sast_job_uses_semgrep(self):
        wf = build_node_workflow(["sast"])
        assert "semgrep" in wf.lower()

    def test_semgrep_uses_config_auto(self):
        wf = build_node_workflow(["sast"])
        assert "--config auto" in wf

    def test_semgrep_has_app_token_env(self):
        wf = build_node_workflow(["sast"])
        assert "SEMGREP_APP_TOKEN" in wf

    def test_semgrep_outputs_sarif(self):
        wf = build_node_workflow(["sast"])
        assert "--sarif" in wf
        assert "semgrep.sarif" in wf

    def test_sast_uploads_sarif_to_github(self):
        wf = build_node_workflow(["sast"])
        assert "upload-sarif" in wf

    def test_sast_has_enforcement_step(self):
        wf = build_node_workflow(["sast"])
        assert "Fail if findings found" in wf
        assert "steps.semgrep.outcome" in wf

    def test_sast_job_has_security_events_write(self):
        wf = build_node_workflow(["sast"])
        assert "security-events: write" in wf

    def test_deps_job_uses_npm_audit(self):
        wf = build_node_workflow(["deps"])
        assert "npm audit" in wf

    def test_secret_scan_job_present_when_selected(self):
        wf = build_node_workflow(["secrets"])
        assert "gitleaks" in wf.lower()

    def test_secret_scan_has_security_events_write(self):
        wf = build_node_workflow(["secrets"])
        assert "security-events: write" in wf

    def test_sast_absent_when_not_selected(self):
        wf = build_node_workflow(["deps"])
        assert "semgrep" not in wf.lower()


# ---------------------------------------------------------------------------
# Node pre-commit
# ---------------------------------------------------------------------------


class TestNodePrecommit:
    def test_detect_secrets_hook_uses_version_constant(self):
        pc = build_node_precommit_config(["secrets", "precommit"])
        assert f"rev: {DETECT_SECRETS}" in pc

    def test_gitleaks_hook_uses_version_constant(self):
        pc = build_node_precommit_config(["secrets", "precommit"])
        assert f"rev: {GITLEAKS}" in pc

    def test_secrets_hooks_included_when_selected(self):
        pc = build_node_precommit_config(["secrets", "precommit"])
        assert "detect-secrets" in pc
        assert "gitleaks" in pc

    def test_npm_audit_hook_included_when_selected(self):
        pc = build_node_precommit_config(["deps", "precommit"])
        assert "npm-audit" in pc

    def test_secrets_hooks_excluded_when_not_selected(self):
        pc = build_node_precommit_config(["deps", "precommit"])
        assert "detect-secrets" not in pc
        assert "gitleaks" not in pc

    def test_empty_repos_when_no_security_layers(self):
        pc = build_node_precommit_config(["precommit"])
        assert pc == "repos: []\n"
