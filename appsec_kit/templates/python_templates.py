_WORKFLOW_HEADER = """\
name: Security Scan

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
"""

_SAST_JOB = """\
  sast:
    name: "SAST - Bandit"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install bandit[toml]
      - run: bandit -r . -x ./tests,./venv,./.venv -f json -o bandit-report.json
        continue-on-error: true
      - uses: actions/upload-artifact@v4
        with:
          name: bandit-report
          path: bandit-report.json
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
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

_PRECOMMIT_SAST = """\
  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        exclude: ^tests/
"""

_PRECOMMIT_SECRETS = """\
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
"""

_PRECOMMIT_DEPS = """\
  - repo: https://github.com/pypa/pip-audit
    rev: v2.7.3
    hooks:
      - id: pip-audit
"""

PYTHON_BANDIT_PYPROJECT_SNIPPET = """
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = []
"""


def build_python_workflow(layers: list[str]) -> str:
    jobs: list[str] = []
    if "sast" in layers:
        jobs.append(_SAST_JOB)
    if "deps" in layers:
        jobs.append(_DEPS_JOB)
    if "secrets" in layers:
        jobs.append(_SECRET_JOB)
    return _WORKFLOW_HEADER + "\n".join(jobs)


def build_python_precommit_config(layers: list[str]) -> str:
    hooks: list[str] = []
    if "sast" in layers:
        hooks.append(_PRECOMMIT_SAST)
    if "secrets" in layers:
        hooks.append(_PRECOMMIT_SECRETS)
    if "deps" in layers:
        hooks.append(_PRECOMMIT_DEPS)
    return "repos:\n" + "".join(hooks) if hooks else "repos: []\n"
