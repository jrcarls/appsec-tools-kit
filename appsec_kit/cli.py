import sys
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel

from .detector import detect_project_type
from .versions import CI_LAYERS
from .writer import write_configs

console = Console()

_LAYER_CHOICES = [
    ("SAST (Static Analysis)", "sast"),
    ("Dependency Scanning", "deps"),
    ("Secret Scanning", "secrets"),
    ("Pre-commit Hooks", "precommit"),
]

_STYLE = questionary.Style([
    ("qmark", "fg:cyan bold"),
    ("question", "bold"),
    ("answer", "fg:cyan bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
    ("instruction", "fg:default dim"),
])


def _print_next_steps(lang: str, layers: list[str]) -> None:
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

    if any(layer in layers for layer in CI_LAYERS) or "precommit" in layers:
        lines += [
            "",
            "# Commit and push to activate GitHub Actions:",
            "git add .github/ .pre-commit-config.yaml",
            'git commit -m "chore: add appsec security configuration"',
            "git push",
        ]

    if lines:
        text = "\n".join(
            f"  {line}" if line and not line.startswith("#") else line for line in lines
        )
        console.print(Panel(
            text,
            title="[bold green]Next steps[/bold green]",
            border_style="green",
            padding=(0, 1),
        ))


def run() -> None:
    console.print()
    console.print(Panel.fit(
        "[bold cyan]AppSec Kit[/bold cyan]  [dim]–  Security toolkit for CI/CD pipelines[/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()

    detected = detect_project_type()
    default_project = {"python": "Python", "node": "Node.js"}.get(detected or "", "Python")

    if detected:
        console.print(f"[dim]Detected:[/dim] [bold]{default_project}[/bold] project\n")

    project_type = questionary.select(
        "Project type:",
        choices=["Python", "Node.js"],
        default=default_project,
        style=_STYLE,
    ).ask()

    if not project_type:
        sys.exit(0)

    target_dir = questionary.text(
        "Target directory:",
        default=".",
        style=_STYLE,
    ).ask()

    if target_dir is None:
        sys.exit(0)

    target_path = Path(target_dir).expanduser().resolve()
    if not target_path.is_dir():
        console.print(f"[red]Error:[/red] '{target_dir}' is not a valid directory.")
        sys.exit(1)

    selected_layers = questionary.checkbox(
        "Security layers to configure:",
        choices=[
            questionary.Choice(label, value=key, checked=True)
            for label, key in _LAYER_CHOICES
        ],
        style=_STYLE,
    ).ask()

    if not selected_layers:
        console.print("[yellow]No layers selected. Exiting.[/yellow]")
        sys.exit(0)

    lang = "python" if project_type == "Python" else "node"

    console.print()
    results = write_configs(target_path, lang, selected_layers)

    for rel_path, status in results:
        color = "green" if status == "created" else "yellow"
        icon = "✓" if status == "created" else "↻"
        console.print(f"  [{color}]{icon}[/{color}]  {rel_path}  [dim]({status})[/dim]")

    console.print()
    _print_next_steps(lang, selected_layers)
