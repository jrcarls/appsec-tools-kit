from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .templates.python_templates import (
    PYTHON_BANDIT_PYPROJECT_SNIPPET,
    build_python_precommit_config,
    build_python_workflow,
)
from .templates.node_templates import (
    build_node_precommit_config,
    build_node_workflow,
)

_CI_LAYERS = frozenset(("sast", "deps", "secrets"))


def write_configs(
    target: Path, lang: str, layers: list[str]
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    ci_layers = [l for l in layers if l in _CI_LAYERS]

    if ci_layers:
        _write_workflow(target, lang, ci_layers, results)

    if "precommit" in layers:
        _write_precommit(target, lang, layers, results)

    return results


def _write_workflow(
    target: Path, lang: str, ci_layers: list[str], results: list[tuple[str, str]]
) -> None:
    path = target / ".github" / "workflows" / "security.yml"
    path.parent.mkdir(parents=True, exist_ok=True)
    build = build_python_workflow if lang == "python" else build_node_workflow
    status = "updated" if path.exists() else "created"
    path.write_text(build(ci_layers))
    results.append((".github/workflows/security.yml", status))


def _write_precommit(
    target: Path, lang: str, layers: list[str], results: list[tuple[str, str]]
) -> None:
    path = target / ".pre-commit-config.yaml"
    build = build_python_precommit_config if lang == "python" else build_node_precommit_config
    status = "updated" if path.exists() else "created"
    path.write_text(build(layers))
    results.append((".pre-commit-config.yaml", status))

    if lang == "python" and "sast" in layers:
        _append_bandit_config(target, results)


def _append_bandit_config(
    target: Path, results: list[tuple[str, str]]
) -> None:
    pyproject = target / "pyproject.toml"
    if not pyproject.exists():
        return
    content = pyproject.read_text()
    if "[tool.bandit]" not in content:
        pyproject.write_text(content + PYTHON_BANDIT_PYPROJECT_SNIPPET)
        results.append(("pyproject.toml", "updated"))


def print_next_steps(console: Console, lang: str, layers: list[str]) -> None:
    lines: list[str] = []

    if "precommit" in layers:
        lines += [
            "pip install pre-commit detect-secrets",
            "detect-secrets scan > .secrets.baseline",
            "pre-commit install",
        ]

    if lang == "node" and "sast" in layers:
        lines += [
            "",
            "# SEMGREP_APP_TOKEN (free) removes API rate limits in CI:",
            "# 1. Create account at https://semgrep.dev",
            "# 2. Go to Settings → Tokens → Create token",
            "# 3. Add to GitHub: Settings → Secrets → SEMGREP_APP_TOKEN",
        ]

    has_ci = any(l in layers for l in _CI_LAYERS)
    if has_ci or "precommit" in layers:
        lines += [
            "",
            "# Commit and push to activate GitHub Actions:",
            "git add .github/ .pre-commit-config.yaml",
            'git commit -m "chore: add appsec security configuration"',
            "git push",
        ]

    if lines:
        text = "\n".join(
            f"  {l}" if l and not l.startswith("#") else l for l in lines
        )
        console.print(Panel(
            text,
            title="[bold green]Next steps[/bold green]",
            border_style="green",
            padding=(0, 1),
        ))
