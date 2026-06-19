from ..versions import DETECT_SECRETS, GITLEAKS

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
    name: "SAST - Semgrep"
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - run: pip install semgrep
      - name: Run Semgrep
        id: semgrep
        run: semgrep scan --config auto --sarif --output semgrep.sarif --error .
        continue-on-error: true
        env:
          SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
      - name: Upload findings to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
          category: semgrep
      - name: Fail if findings found
        if: steps.semgrep.outcome == 'failure'
        run: |
          echo "Semgrep found security issues. Check the Security tab."
          exit 1
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

_PRECOMMIT_SECRETS = f"""\
  - repo: https://github.com/Yelp/detect-secrets
    rev: {DETECT_SECRETS}
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
"""

_PRECOMMIT_GITLEAKS = f"""\
  - repo: https://github.com/gitleaks/gitleaks
    rev: {GITLEAKS}
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

_WORKFLOW_JOBS: dict[str, str] = {
    "sast": _SAST_JOB,
    "deps": _DEPS_JOB,
    "secrets": _SECRET_JOB,
}

_PRECOMMIT_HOOKS: dict[str, str] = {
    "secrets": _PRECOMMIT_SECRETS + _PRECOMMIT_GITLEAKS,
    "deps": _PRECOMMIT_DEPS,
}


def build_node_workflow(layers: list[str]) -> str:
    jobs = [_WORKFLOW_JOBS[layer] for layer in layers if layer in _WORKFLOW_JOBS]
    return _WORKFLOW_HEADER + "\n".join(jobs)


def build_node_precommit_config(layers: list[str]) -> str:
    hooks = [_PRECOMMIT_HOOKS[layer] for layer in layers if layer in _PRECOMMIT_HOOKS]
    return "repos:\n" + "".join(hooks) if hooks else "repos: []\n"
