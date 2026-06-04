# main.py
# SIFT-BENCH: Main Entry Point
# Run this to start the autonomous IR analysis

import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from agent.agent import IRAgent
from evaluator.evaluator import Evaluator
from reporter.reporter import Reporter

load_dotenv()

console = Console()

def main():
    console.print(Panel.fit(
        "[bold green]SIFT-BENCH: Autonomous IR Analysis System[/bold green]\n"
        "[yellow]Benchmarking AI accuracy in incident response[/yellow]",
        border_style="green"
    ))

    # Configuration
    evidence_path = "test_cases/evidence/case001"
    ground_truth_path = "test_cases/ground_truth.json"

    console.print(f"\n[cyan]Evidence Path:[/cyan] {evidence_path}")
    console.print(f"[cyan]Ground Truth:[/cyan] {ground_truth_path}\n")

    # Step 1: Run IR Agent
    console.print("[bold yellow]Step 1: Running Autonomous IR Agent...[/bold yellow]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing evidence...", total=None)
        agent = IRAgent(evidence_path, max_iterations=5)
        agent_result = agent.run()
        progress.stop()

    if not agent_result.get("success"):
        console.print(f"[red]Agent failed: {agent_result.get('error')}[/red]")
        return

    console.print("[green]✓ Agent analysis complete![/green]")
    console.print(f"[cyan]Duration:[/cyan] {agent_result.get('duration_seconds', 0):.2f}s")
    console.print(f"[cyan]Iterations:[/cyan] {agent_result.get('iterations_completed', 0)}")

    # Step 2: Evaluate Accuracy
    console.print("\n[bold yellow]Step 2: Evaluating Accuracy Against Ground Truth...[/bold yellow]")
    evaluator = Evaluator(ground_truth_path)
    eval_result = evaluator.evaluate(agent_result)

    console.print("[green]✓ Evaluation complete![/green]")
    console.print(f"[cyan]Accuracy Score:[/cyan] {eval_result.get('accuracy_score')}%")
    console.print(f"[cyan]Hallucination Rate:[/cyan] {eval_result.get('hallucination_rate')}%")
    console.print(f"[cyan]Grade:[/cyan] {eval_result.get('grade')}")

    # Step 3: Generate Report
    console.print("\n[bold yellow]Step 3: Generating Final Report...[/bold yellow]")
    reporter = Reporter()
    final_report = reporter.generate_full_report(
        agent_result,
        eval_result,
        agent_result.get("session_id", "unknown")
    )

    console.print("[green]✓ Report generated![/green]")
    console.print("\n" + "="*60)
    console.print(final_report)
    console.print("="*60)

    console.print(Panel.fit(
        f"[bold green]Analysis Complete![/bold green]\n"
        f"Accuracy: {eval_result.get('accuracy_score')}% | "
        f"Hallucinations: {eval_result.get('hallucination_rate')}% | "
        f"Grade: {eval_result.get('grade')}",
        border_style="green"
    ))

if __name__ == "__main__":
    main()