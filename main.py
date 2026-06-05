import os
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from agent.agent import IRAgent
from evaluator.evaluator import Evaluator
from reporter.reporter import Reporter

load_dotenv()

console = Console()

def run_case(evidence_path, ground_truth_path, case_name):
    console.print(Panel.fit(
        f"[bold green]SIFT-BENCH: Autonomous IR Analysis System[/bold green]\n"
        f"[yellow]Case: {case_name}[/yellow]",
        border_style="green"
    ))

    console.print(f"\n[cyan]Evidence Path:[/cyan] {evidence_path}")
    console.print(f"[cyan]Ground Truth:[/cyan] {ground_truth_path}\n")

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

    console.print("\n[bold yellow]Step 2: Evaluating Accuracy Against Ground Truth...[/bold yellow]")
    evaluator = Evaluator(ground_truth_path)
    eval_result = evaluator.evaluate(agent_result)

    console.print("[green]✓ Evaluation complete![/green]")
    console.print(f"[cyan]Accuracy Score:[/cyan] {eval_result.get('accuracy_score')}%")
    console.print(f"[cyan]Hallucination Rate:[/cyan] {eval_result.get('hallucination_rate')}%")
    console.print(f"[cyan]Grade:[/cyan] {eval_result.get('grade')}")

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
        f"[bold green]{case_name} Complete![/bold green]\n"
        f"Accuracy: {eval_result.get('accuracy_score')}% | "
        f"Hallucinations: {eval_result.get('hallucination_rate')}% | "
        f"Grade: {eval_result.get('grade')}",
        border_style="green"
    ))

    return eval_result

def main():
    # Run Case 001 - Malware
    result1 = run_case(
        "test_cases/evidence/case001",
        "test_cases/ground_truth.json",
        "CASE-001: Malware Infection"
    )

    console.print("\n" + "="*60 + "\n")

    # Run Case 002 - Ransomware
    result2 = run_case(
        "test_cases/evidence/case002",
        "test_cases/ground_truth_case002.json",
        "CASE-002: Ransomware Attack"
    )

    # Final summary
    if result1 and result2:
        avg_accuracy = (result1.get('accuracy_score', 0) + result2.get('accuracy_score', 0)) / 2
        avg_hallucination = (result1.get('hallucination_rate', 0) + result2.get('hallucination_rate', 0)) / 2
        console.print(Panel.fit(
            f"[bold green]OVERALL RESULTS — 2 CASES[/bold green]\n"
            f"Average Accuracy: {avg_accuracy:.1f}% | "
            f"Average Hallucinations: {avg_hallucination:.1f}%",
            border_style="green"
        ))

if __name__ == "__main__":
    main()
