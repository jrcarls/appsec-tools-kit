from pathlib import Path

_PYTHON_MARKERS = ("pyproject.toml", "setup.py", "requirements.txt", "Pipfile")
_NODE_MARKERS = ("package.json",)


def detect_project_type(path: Path | None = None) -> str | None:
    """Return 'python', 'node', or None when both or neither are detected."""
    target = path or Path.cwd()
    has_python = any((target / f).exists() for f in _PYTHON_MARKERS)
    has_node = any((target / f).exists() for f in _NODE_MARKERS)
    if has_python and not has_node:
        return "python"
    if has_node and not has_python:
        return "node"
    return None
