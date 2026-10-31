"""
RepairForge AI command-line interface.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from repairforge import __version__
from repairforge.agent.orchestrator import RepairOrchestrator
from repairforge.config import AppConfig, ProviderConfig
from repairforge.evaluation.reporter import RepairReporter
from repairforge.investigation.issue_parser import IssueParser
from repairforge.repository.analyzer import RepositoryAnalyzer

app = typer.Typer(
    name="repairforge",
    help="Investigate. Reproduce. Repair. Verify. Open-weight code-repair agent harness.",
    add_completion=False,
)
skill_app = typer.Typer(help="Manage and validate Agent Skills.")
app.add_typer(skill_app, name="skill")

console = Console()


@app.command()
def version() -> None:
    """Print the version of RepairForge AI."""
    console.print(f"[bold cyan]RepairForge AI[/bold cyan] version [green]{__version__}[/green]")


@app.command()
def inspect(
    repo: Path = typer.Option(
        Path("."),
        "--repo",
        "-r",
        help="Path to repository to inspect",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
) -> None:
    """Inspect repository structure, detected languages, and dependencies."""
    try:
        analyzer = RepositoryAnalyzer(repo)
        summary = analyzer.analyze()

        table = Table(title=f"Repository Inspection: {summary.root_path.name}")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Root Path", str(summary.root_path))
        table.add_row("Total Files", str(summary.total_files))
        table.add_row("Languages", ", ".join(summary.languages) if summary.languages else "None detected")
        table.add_row("Git Repository", "Yes" if summary.has_git else "No")
        table.add_row("Has Tests", "Yes" if summary.has_tests else "No")
        table.add_row("Test Framework", summary.test_framework or "None detected")
        table.add_row("Dependencies", ", ".join(summary.dependency_files) if summary.dependency_files else "None")

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error inspecting repository:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def demo() -> None:
    """
    Run deterministic end-to-end bug repair demonstration on the buggy average fixture.
    Shows failure reproduction, root cause analysis, mock patch generation,
    and verified test passing.
    """
    console.print(
        Panel.fit(
            "[bold cyan]RepairForge AI — Deterministic Repair Demonstration[/bold cyan]\n"
            "[yellow]Note: Inference is performed deterministically by MockModelAdapter (Not an LLM)[/yellow]",
            border_style="cyan",
        )
    )

    fixture_dir = Path(__file__).resolve().parent.parent / "examples" / "buggy_average"
    if not fixture_dir.exists():
        # Look in current working directory
        fixture_dir = Path("examples") / "buggy_average"

    if not fixture_dir.exists():
        console.print(f"[bold red]Demo fixture directory not found at {fixture_dir}[/bold red]")
        raise typer.Exit(code=1)

    bug_report_path = fixture_dir / "bug_report.md"
    if not bug_report_path.exists():
        console.print(f"[bold red]Bug report not found at {bug_report_path}[/bold red]")
        raise typer.Exit(code=1)

    bug_report = IssueParser.parse(bug_report_path.read_text(encoding="utf-8"))

    # Configure orchestrator with auto-approval for non-interactive demo
    config = AppConfig()
    config.agent.auto_approve_human_review = True
    config.provider.provider_type = "mock"

    orchestrator = RepairOrchestrator(config=config)

    with console.status("[bold green]Running RepairForge workflow...[/bold green]") as status:
        context = orchestrator.run(
            repo_path=fixture_dir,
            bug_report=bug_report,
            test_command="python -m pytest test_average.py",
            isolate_workspace=True,
            human_approval_callback=True,
        )

    # Print summary
    report_status = RepairReporter.determine_status(context)
    color = "green" if report_status == "VERIFIED" else "red"

    console.print(f"\n[bold]Demonstration Outcome:[/bold] [{color}]{report_status}[/{color}]")
    console.print(f"Task ID: [cyan]{context.task_id}[/cyan]")

    if context.reproduction_result:
        console.print(
            f"Reproduction: [yellow]{context.reproduction_result.status}[/yellow] "
            f"(Exit code {context.reproduction_result.exit_code})"
        )

    if context.root_cause_analysis:
        console.print(f"Root Cause: [magenta]{context.root_cause_analysis.explanation}[/magenta]")

    if context.patch:
        console.print("\n[bold]Generated Unified Diff:[/bold]")
        console.print(f"[dim]{context.patch.diff}[/dim]")

    if context.verification_result:
        verif_color = "green" if context.verification_result.verified else "red"
        console.print(
            f"\nVerification Tests: [{verif_color}]"
            f"{'PASSED' if context.verification_result.verified else 'FAILED'}[/{verif_color}]"
        )

    out_md = config.agent.output_dir / f"repair_report_{context.task_id}.md"
    console.print(f"\nReport written to: [bold underline]{out_md}[/bold underline]")

    if report_status != "VERIFIED":
        raise typer.Exit(code=1)


@skill_app.command("validate")
def skill_validate(
    skill_path: Path = typer.Option(
        Path("skills") / "bugrepro",
        "--path",
        "-p",
        help="Path to the Agent Skill directory",
    ),
) -> None:
    """Validate that an Agent Skill package complies with the Agent Skills specification."""
    if not skill_path.exists() or not skill_path.is_dir():
        console.print(f"[bold red]Skill directory not found:[/bold red] {skill_path}")
        raise typer.Exit(code=1)

    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        console.print(f"[bold red]Missing SKILL.md in {skill_path}[/bold red]")
        raise typer.Exit(code=1)

    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        console.print("[bold red]SKILL.md missing YAML frontmatter opening '---'[/bold red]")
        raise typer.Exit(code=1)

    parts = content.split("---", 2)
    if len(parts) < 3:
        console.print("[bold red]SKILL.md malformed YAML frontmatter[/bold red]")
        raise typer.Exit(code=1)

    try:
        meta = yaml.safe_load(parts[1])
    except Exception as e:
        console.print(f"[bold red]Invalid YAML in SKILL.md frontmatter:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not isinstance(meta, dict):
        console.print("[bold red]Frontmatter must parse to a dictionary[/bold red]")
        raise typer.Exit(code=1)

    name = meta.get("name")
    desc = meta.get("description")

    if not name:
        console.print("[bold red]Skill metadata missing 'name'[/bold red]")
        raise typer.Exit(code=1)

    expected_name = skill_path.name
    if name != expected_name:
        console.print(
            f"[bold red]Skill name '{name}' does not match parent directory name '{expected_name}'[/bold red]"
        )
        raise typer.Exit(code=1)

    if not desc:
        console.print("[bold red]Skill metadata missing 'description'[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Skill '{name}' is valid according to Agent Skills standard.[/bold green]")
    console.print(f"Description: {desc.strip()[:100]}...")


@app.command()
def report(
    latest: bool = typer.Option(True, "--latest", help="Show the latest repair report"),
    results_dir: Path = typer.Option(Path("results"), "--dir", "-d", help="Results directory"),
) -> None:
    """Display the latest repair report."""
    if not results_dir.exists():
        console.print(f"[bold red]Results directory not found:[/bold red] {results_dir}")
        raise typer.Exit(code=1)

    md_reports = sorted(results_dir.glob("repair_report_*.md"), key=os.path.getmtime, reverse=True)
    if not md_reports:
        console.print("[yellow]No repair reports found in results directory.[/yellow]")
        raise typer.Exit(code=0)

    target_report = md_reports[0]
    console.print(f"[bold cyan]Showing latest report:[/bold cyan] {target_report.name}\n")
    console.print(target_report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()

