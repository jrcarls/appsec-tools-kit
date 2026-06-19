from unittest.mock import patch

from rich.panel import Panel

from appsec_kit.cli import _print_next_steps


def _capture(lang: str, layers: list[str]) -> str:
    captured: list[str] = []

    def _collect(*args, **_):
        for arg in args:
            if isinstance(arg, Panel):
                captured.append(str(arg.renderable))
            else:
                captured.append(str(arg))

    with patch("appsec_kit.cli.console") as mock_console:
        mock_console.print.side_effect = _collect
        _print_next_steps(lang, layers)
    return "\n".join(captured)


class TestNextSteps:
    def test_precommit_with_secrets_shows_baseline_and_detect_secrets(self):
        out = _capture("python", ["precommit", "secrets"])
        assert "detect-secrets scan" in out
        assert "detect-secrets" in out
        assert "pre-commit install" in out

    def test_precommit_without_secrets_omits_baseline_and_detect_secrets_pkg(self):
        out = _capture("python", ["precommit", "sast"])
        assert "detect-secrets scan" not in out
        assert "detect-secrets" not in out
        assert "pre-commit install" in out

    def test_precommit_only_omits_baseline(self):
        out = _capture("python", ["precommit"])
        assert "detect-secrets scan" not in out
        assert "pre-commit install" in out

    def test_no_precommit_shows_nothing(self):
        out = _capture("python", ["sast", "deps", "secrets"])
        assert "pre-commit install" not in out
        assert "detect-secrets scan" not in out

    def test_node_sast_shows_semgrep_token_instructions(self):
        out = _capture("node", ["sast", "precommit"])
        assert "SEMGREP_APP_TOKEN" in out

    def test_python_sast_omits_semgrep_token_instructions(self):
        out = _capture("python", ["sast", "precommit"])
        assert "SEMGREP_APP_TOKEN" not in out

    def test_ci_layers_show_git_push_instructions(self):
        out = _capture("python", ["sast"])
        assert "git push" in out

    def test_no_layers_shows_nothing(self):
        out = _capture("python", [])
        assert out == ""
