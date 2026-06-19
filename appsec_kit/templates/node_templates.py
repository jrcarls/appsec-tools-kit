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
    name: "SAST - Semgrep"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - run: pip install semgrep
      - run: semgrep --config=p/javascript --config=p/nodejs --config=p/typescript .
"""

_DEPS_JOB = """\
  dependency-scan:
    name: "Dependency Scan - npm audit"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm audit --audit-level=high
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

_PRECOMMIT_SECRETS = """\
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
"""

_PRECOMMIT_GITLEAKS = """\
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.1
    hooks:
      - id: gitleaks
"""

_PRECOMMIT_DEPS = """\
  - repo: local
    hooks:
      - id: npm-audit
        name: npm audit
        entry: npm audit --audit-level=high
        language: system
        pass_filenames: false
        files: package\\.json
"""


def build_node_workflow(layers: list[str]) -> str:
    jobs: list[str] = []
    if "sast" in layers:
        jobs.append(_SAST_JOB)
    if "deps" in layers:
        jobs.append(_DEPS_JOB)
    if "secrets" in layers:
        jobs.append(_SECRET_JOB)
    return _WORKFLOW_HEADER + "\n".join(jobs)


def build_node_precommit_config(layers: list[str]) -> str:
    hooks: list[str] = []
    if "secrets" in layers:
        hooks.append(_PRECOMMIT_SECRETS)
        hooks.append(_PRECOMMIT_GITLEAKS)
    if "deps" in layers:
        hooks.append(_PRECOMMIT_DEPS)
    return "repos:\n" + "".join(hooks) if hooks else "repos: []\n"
