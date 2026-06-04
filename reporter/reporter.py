# reporter/reporter.py
# SIFT-BENCH: Report Generator
# Produces professional IR reports with accuracy scores

import json
import os
from datetime import datetime
from loguru import logger

class Reporter:
    """
    Generates professional IR reports.
    Combines agent findings with accuracy evaluation.
    """

    def __init__(self):
        os.makedirs("reports", exist_ok=True)
        logger.info("Reporter initialized")

    def generate_full_report(self, agent_result: dict, 
                              eval_result: dict, 
                              session_id: str) -> str:
        """Generate complete report combining agent + evaluator results."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %Human:%M:%S")
        accuracy = eval_result.get("accuracy_score", 0)
        hallucination_rate = eval_result.get("hallucination_rate", 0)
        grade = eval_result.get("grade", "UNKNOWN")
        duration = agent_result.get("duration_seconds", 0)
        iterations = agent_result.get("iterations_completed", 0)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           SIFT-BENCH INCIDENT RESPONSE REPORT                ║
║              Autonomous IR Analysis System                    ║
╚══════════════════════════════════════════════════════════════╝

Session ID:     {session_id}
Generated:      {timestamp}
Duration:       {duration:.2f} seconds
Iterations:     {iterations}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    ACCURACY SCORECARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Accuracy:       {accuracy:.1f}%
Hallucination Rate:     {hallucination_rate:.1f}%
True Positives:         {eval_result.get('true_positives', 0)}
False Negatives:        {eval_result.get('false_negatives', 0)}
Hallucinations:         {eval_result.get('hallucinations', 0)}
Performance Grade:      {grade}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    AGENT IR REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{agent_result.get('final_report', 'No report generated')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CONFIRMED FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._format_findings(eval_result.get('true_positive_details', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    MISSED FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._format_findings(eval_result.get('false_negative_details', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    HALLUCINATIONS DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._format_findings(eval_result.get('hallucination_details', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    EXECUTION TRACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._format_trace(agent_result.get('execution_trace', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
END OF REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # Save report
        report_path = f"reports/report_{session_id}.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved: {report_path}")
        return report

    def _format_findings(self, findings: list) -> str:
        if not findings:
            return "  None"
        lines = []
        for f in findings:
            lines.append(f"  ✓ {f.get('keyword', '')} — {f.get('description', '')}")
        return "\n".join(lines)

    def _format_trace(self, trace: list) -> str:
        if not trace:
            return "  No trace available"
        lines = []
        for entry in trace:
            lines.append(
                f"  [{entry.get('timestamp', '')}] "
                f"Iter {entry.get('iteration', '')} | "
                f"Tool: {entry.get('tool', '')} | "
                f"Result: {entry.get('result_summary', '')[:100]}"
            )
        return "\n".join(lines)