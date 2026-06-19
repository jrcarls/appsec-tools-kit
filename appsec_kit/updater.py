import json
import re
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from rich.console import Console

console = Console()

_VERSIONS_PATH = Path(__file__).parent / "versions.py"

# (github_repo, keep_v_prefix)
_TOOLS: dict[str, tuple[str, bool]] = {
    "BANDIT": ("PyCQA/bandit", False),
    "DETECT_SECRETS": ("Yelp/detect-secrets", True),
    "PIP_AUDIT": ("pypa/pip-audit", True),
    "GITLEAKS": ("gitleaks/gitleaks", True),
}


def _fetch_latest_tag(repo: str) -> str | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("tag_name")
    except (URLError, json.JSONDecodeError, KeyError):
        return None


def bump_versions() -> None:
    console.print()
    console.print("[bold]Checking latest versions...[/bold]\n")

    content = _VERSIONS_PATH.read_text()
    updated = content
    any_change = False

    for var, (repo, keep_v) in _TOOLS.items():
        tag = _fetch_latest_tag(repo)
        if tag is None:
            console.print(f"  [yellow]⚠[/yellow]  {var}: could not fetch from {repo}")
            continue

        version = tag if keep_v else tag.lstrip("v")

        match = re.search(rf'^{var} = "([^"]+)"', content, re.MULTILINE)
        if not match:
            console.print(f"  [yellow]⚠[/yellow]  {var}: not found in versions.py")
            continue

        current = match.group(1)
        if current == version:
            console.print(f"  [dim]–[/dim]  {var}: [dim]{current} (up to date)[/dim]")
        else:
            updated = updated.replace(f'{var} = "{current}"', f'{var} = "{version}"')
            console.print(f"  [green]↑[/green]  {var}: [dim]{current}[/dim] → [bold green]{version}[/bold green]")
            any_change = True

    console.print()

    if any_change:
        _VERSIONS_PATH.write_text(updated)
        console.print("[green]versions.py updated.[/green] Commit when pronto:")
        console.print('  [dim]git add appsec_kit/versions.py[/dim]')
        console.print('  [dim]git commit -m "chore: bump pinned tool versions"[/dim]')
    else:
        console.print("[dim]All versions up to date.[/dim]")

    console.print()
