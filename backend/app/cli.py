import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console(force_terminal=True, legacy_windows=False)

from app.database import SessionLocal, init_db
from app.routers.scans import run_scan
from app.schemas import ScanRequest

@click.group()
def cli():
    """CodeGuardian CLI — Smart bug detection, SCA security & quality analyzer."""
    pass

@cli.command()
@click.argument("target_path", default=".", type=click.Path(exists=True))
@click.option("--name", default="CLI Scan", help="Project name")
@click.option("--fail-on-critical/--no-fail-on-critical", default=True, help="Exit with non-zero code if critical bugs are found")
@click.option("--ai-fixes/--no-ai-fixes", default=True, help="Generate AI remediation and diffs")
@click.option("--diff-only", is_flag=True, default=False, help="Only scan files modified in Git working tree or PR diff")
@click.option("--output", default=None, help="Save report to file (e.g. report.md, report.json)")
def scan(target_path, name, fail_on_critical, ai_fixes, diff_only, output):
    """Scan a codebase for bugs, code smells, duplications, SCA CVEs, and hotspot risks."""
    init_db()
    db = SessionLocal()
    target_abs = str(Path(target_path).resolve())

    console.print(Panel(
        f"[bold cyan]CodeGuardian Analysis Engine[/bold cyan]\nTarget: [yellow]{target_abs}[/yellow]{' (Diff-Only PR mode)' if diff_only else ''}",
        border_style="cyan"
    ))

    with console.status("[bold green]Analyzing AST, dependencies SCA, calculating metrics, detecting duplications & AI predictions..."):
        try:
            req = ScanRequest(target_path=target_abs, project_name=name, include_ai_fixes=ai_fixes, diff_only=diff_only)
            result = run_scan(req, db)
        except Exception as e:
            console.print(f"[bold red]Scan failed:[/bold red] {e}")
            sys.exit(2)
        finally:
            db.close()

    # Display Metrics Table
    health_color = "green" if result.health_score >= 80 else "yellow" if result.health_score >= 60 else "red"
    console.print(f"\n[bold]Health Score:[/bold] [{health_color}]{result.health_score} / 100[/{health_color}]")
    console.print(f"[bold]Total Files:[/bold] {result.total_files} | [bold]LOC:[/bold] {result.lines_of_code} | [bold]Duplication:[/bold] {result.duplication_percentage}%")
    console.print(f"[bold]Issues:[/bold] [red]{result.critical_count} Critical[/red] | [yellow]{result.high_count} High[/yellow] | [blue]{result.medium_count} Medium[/blue] | [dim]{result.low_count} Low[/dim]")

    # Defects Table
    if result.defects:
        table = Table(title="Detected Issues, Security Defects & SCA Vulnerabilities", show_lines=True)
        table.add_column("Severity", style="bold")
        table.add_column("Rule", style="cyan")
        table.add_column("Location")
        table.add_column("Description")

        for d in result.defects[:15]:
            sev_style = "red" if d.severity == "CRITICAL" else "yellow" if d.severity == "HIGH" else "blue"
            table.add_row(
                f"[{sev_style}]{d.severity}[/{sev_style}]",
                d.rule_id,
                f"{d.file_path}:{d.line_number}",
                d.title
            )
        console.print(table)
        if len(result.defects) > 15:
            console.print(f"[dim]...and {len(result.defects) - 15} more defects (view in dashboard)[/dim]")

    # Hotspots Table
    if result.hotspots:
        htable = Table(title="Defect Risk Predictions (Hotspots)", show_lines=True)
        htable.add_column("Risk Level", style="bold")
        htable.add_column("Risk Score")
        htable.add_column("File", style="cyan")
        htable.add_column("Primary Risk Factor")

        for h in result.hotspots[:5]:
            color = "red" if h.risk_level in ("CRITICAL", "HIGH") else "yellow" if h.risk_level == "MEDIUM" else "green"
            reasons = ", ".join(h.reasons[:2]) if h.reasons else "Normal"
            htable.add_row(
                f"[{color}]{h.risk_level}[/{color}]",
                str(h.risk_score),
                h.file_path,
                reasons
            )
        console.print(htable)

    # Save output if requested
    if output:
        out_p = Path(output)
        if out_p.suffix.lower() == ".json":
            out_p.write_text(result.json(), encoding="utf-8")
        else:
            # Markdown summary
            md_lines = [
                f"# CodeGuardian Scan Report",
                f"- Health Score: **{result.health_score}/100**",
                f"- Total Issues: {result.total_issues}",
                f"- Critical: {result.critical_count}, High: {result.high_count}",
                f"- Duplication: {result.duplication_percentage}%"
            ]
            out_p.write_text("\n".join(md_lines), encoding="utf-8")
        console.print(f"[green]Report saved to {output}[/green]")

    # Exit code
    if fail_on_critical and result.critical_count > 0:
        console.print(f"[bold red]Quality Gate Failed:[/bold red] {result.critical_count} critical issues found.")
        sys.exit(1)
    else:
        console.print("[bold green]Scan passed successfully![/bold green]")
        sys.exit(0)

if __name__ == "__main__":
    cli()
