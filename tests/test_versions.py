import re

from appsec_kit.versions import BANDIT, CI_LAYERS, DETECT_SECRETS, GITLEAKS, PIP_AUDIT

_SEMVER_RE = re.compile(r"^v?\d+\.\d+(\.\d+)?$")


def test_all_tool_versions_are_strings():
    for version in (BANDIT, DETECT_SECRETS, PIP_AUDIT, GITLEAKS):
        assert isinstance(version, str)


def test_all_tool_versions_match_semver():
    for version in (BANDIT, DETECT_SECRETS, PIP_AUDIT, GITLEAKS):
        assert _SEMVER_RE.match(version), f"Unexpected version format: {version!r}"


def test_ci_layers_contains_expected_values():
    assert CI_LAYERS == frozenset({"sast", "deps", "secrets"})


def test_ci_layers_is_frozen():
    assert isinstance(CI_LAYERS, frozenset)
