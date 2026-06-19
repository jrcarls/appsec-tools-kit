from ..versions import BANDIT, DETECT_SECRETS, PIP_AUDIT

_WORKFLOW_HEADER = """\
name: Security Scan

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

permissions:
  contents: read

jobs:
"""

_SAST_JOB = """\
  sast:
    name: "SAST - Bandit"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install bandit[toml]
      - name: Run Bandit
        id: bandit
        run: bandit -r . -x ./tests,./venv,./.venv -ll -f sarif -o bandit.sarif
        continue-on-error: true
      - name: Upload findings to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: bandit.sarif
          category: bandit
      - name: Fail if findings found
        if: steps.bandit.outcome == 'failure'
        run: |
          echo "Bandit found security issues (medium severity or above). Check the Security tab."
          exit 1
"""

_DEPS_JOB = """\
  dependency-scan:
    name: "Dependency Scan - pip-audit"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit
"""

_SECRET_JOB = """\
  secret-scan:
    name: "Secret Scanning - Gitleaks"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

_PRECOMMIT_SAST = f"""\
  - repo: https://github.com/PyCQA/bandit
    rev: {BANDIT}
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        exclude: ^tests/
"""

_PRECOMMIT_SECRETS = f"""\
  - repo: https://github.com/Yelp/detect-secrets
    rev: {DETECT_SECRETS}
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
"""

_PRECOMMIT_DEPS = f"""\
  - repo: https://github.com/pypa/pip-audit
    rev: {PIP_AUDIT}
    hooks:
      - id: pip-audit
"""

PYTHON_BANDIT_PYPROJECT_SNIPPET = """
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = []
"""

_WORKFLOW_JOBS: dict[str, str] = {
    "sast": _SAST_JOB,
    "deps": _DEPS_JOB,
    "secrets": _SECRET_JOB,
}

_PRECOMMIT_HOOKS: dict[str, str] = {
    "sast": _PRECOMMIT_SAST,
    "secrets": _PRECOMMIT_SECRETS,
    "deps": _PRECOMMIT_DEPS,
}


def build_python_workflow(layers: list[str]) -> str:
    jobs = [_WORKFLOW_JOBS[layer] for layer in layers if layer in _WORKFLOW_JOBS]
    return _WORKFLOW_HEADER + "\n".join(jobs)


def build_python_precommit_config(layers: list[str]) -> str:
    hooks = [_PRECOMMIT_HOOKS[layer] for layer in layers if layer in _PRECOMMIT_HOOKS]
    return "repos:\n" + "".join(hooks) if hooks else "repos: []\n"
