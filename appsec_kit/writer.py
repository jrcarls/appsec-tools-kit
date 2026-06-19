from pathlib import Path

from .templates.python_templates import (
    PYTHON_BANDIT_PYPROJECT_SNIPPET,
    build_python_precommit_config,
    build_python_workflow,
)
from .templates.node_templates import (
    build_node_precommit_config,
    build_node_workflow,
)
from .versions import CI_LAYERS


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


