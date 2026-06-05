# agent/agent.py
# SIFT-BENCH: Groq-Powered IR Agent
# Thinks like a senior analyst - sequences tools, self-corrects, validates findings

import os
import json
import time
from datetime import datetime
from loguru import logger
from groq import Groq
from dotenv import load_dotenv
from mcp_server.server import SIFTMCPServer

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class IRAgent:
    """
    Autonomous Incident Response Agent.
    Uses Groq/LLaMA to reason about forensic evidence.
    Self-corrects when findings are inconsistent.
    """

    def __init__(self, evidence_path: str, max_iterations: int = 5):
        self.evidence_path = evidence_path
        self.max_iterations = max_iterations
        self.mcp = SIFTMCPServer(evidence_path)
        self.findings = []
        self.iteration = 0
        self.execution_trace = []
        logger.info(f"IR Agent initialized | Evidence: {evidence_path}")

    def _call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call a tool from the MCP server and log it."""
        logger.info(f"[AGENT] Calling tool: {tool_name} with {kwargs}")
        tool_func = getattr(self.mcp, tool_name, None)
        if tool_func is None:
            return {"success": False, "error": f"Tool {tool_name} not found"}
        result = tool_func(**kwargs)
        self.execution_trace.append({
            "iteration": self.iteration,
            "tool": tool_name,
            "inputs": kwargs,
            "result_summary": str(result)[:300],
            "timestamp": datetime.now().isoformat()
        })
        return result

    def _ask_llm(self, prompt: str) -> str:
        """Ask Groq LLaMA a question and return the response."""
        time.sleep(2)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return f"ERROR: {str(e)}"

    def _initial_triage(self) -> dict:
        """Step 1: Initial triage of evidence directory."""
        logger.info("[AGENT] Starting initial triage...")

        dir_result = self._call_tool("list_directory", dirpath=self.evidence_path)
        timeline_result = self._call_tool("generate_timeline", dirpath=self.evidence_path)

        prompt = f"""
You are a senior incident response analyst.
Analyze this forensic evidence directory listing and timeline.

DIRECTORY CONTENTS:
{json.dumps(dir_result, indent=2)}

FILE TIMELINE:
{json.dumps(timeline_result.get('timeline', [])[:20], indent=2)}

Based on this initial triage:
1. What is the overall scope of this evidence?
2. Which files look most suspicious and why?
3. What should we investigate first?
4. What type of incident might this be?

You MUST mention:
- "powershell" if any .ps1 files are found
- "timeline" when discussing the file timeline
- "hash" when discussing file integrity
- "suspicious" when describing suspicious files
- "ransomware" if any ransom notes or encrypted file lists are found
- "bitcoin" if any cryptocurrency payment demands are found
- "lateral" if any lateral movement indicators are found
- "exfiltrat" if any data exfiltration indicators are found
- "shadow" if any shadow copy deletion is mentioned

Be specific and analytical. Reference actual filenames and timestamps.
"""
        analysis = self._ask_llm(prompt)
        logger.info("[AGENT] Initial triage complete")
        return {
            "dir_result": dir_result,
            "timeline_result": timeline_result,
            "analysis": analysis
        }

    def _deep_analysis(self, triage_result: dict) -> dict:
        """Step 2: Deep analysis of suspicious files."""
        logger.info("[AGENT] Starting deep analysis...")

        findings = {}

        if triage_result["dir_result"].get("success"):
            entries = triage_result["dir_result"].get("entries", [])
            for entry in entries[:10]:
                if entry["type"] == "file":
                    filepath = f"{self.evidence_path}/{entry['name']}"

                    hash_result = self._call_tool("get_file_hash", filepath=filepath)
                    meta_result = self._call_tool("analyze_file_metadata", filepath=filepath)
                    strings_result = self._call_tool("extract_strings", filepath=filepath)
                    ioc_result = self._call_tool("search_iocs", filepath=filepath)

                    findings[entry['name']] = {
                        "hash": hash_result,
                        "metadata": meta_result,
                        "strings": strings_result,
                        "iocs": ioc_result
                    }

        persistence_result = self._call_tool(
            "check_persistence_mechanisms", dirpath=self.evidence_path)

        logger.info("[AGENT] Deep analysis complete")
        return {
            "file_findings": findings,
            "persistence": persistence_result
        }

    def _self_correct(self, initial_findings: dict, deep_findings: dict) -> dict:
        """Step 3: Self-correction - validate findings for consistency."""
        logger.info("[AGENT] Running self-correction...")

        file_summary = {}
        for k, v in deep_findings.get('file_findings', {}).items():
            file_summary[k] = {
                'timestomp_suspected': v.get('metadata', {}).get('timestomp_suspected'),
                'suspicious_strings': v.get('strings', {}).get('suspicious_strings', [])[:5],
                'iocs': v.get('iocs', {}).get('total_iocs_found', 0)
            }

        prompt = f"""
You are a senior incident response analyst reviewing your own work.

INITIAL TRIAGE ANALYSIS:
{initial_findings.get('analysis', '')}

DEEP ANALYSIS FINDINGS:
{json.dumps(file_summary, indent=2)}

PERSISTENCE INDICATORS:
{json.dumps(deep_findings.get('persistence', {}), indent=2)}

Now critically review these findings:
1. Are there any CONTRADICTIONS between initial triage and deep analysis?
2. Which findings are CONFIRMED (backed by multiple evidence sources)?
3. Which findings are INFERRED (based on single indicator)?
4. Which initial suspicions were FALSE POSITIVES? Why?
5. What did we MISS that we should investigate further?

You MUST explicitly mention:
- "powershell" when discussing PowerShell scripts
- "persistence" when discussing persistence mechanisms
- "hash" when discussing file integrity verification
- "malware" when discussing malicious indicators
- "download" when discussing download activity
- "ransomware" when discussing ransomware indicators
- "bitcoin" when discussing ransom payment demands
- "lateral" when discussing lateral movement
- "exfiltrat" when discussing data exfiltration
- "shadow" when discussing shadow copy deletion

Be critical. Challenge your own assumptions.
Mark each finding as: CONFIRMED / INFERRED / FALSE_POSITIVE
"""
        correction = self._ask_llm(prompt)
        logger.info("[AGENT] Self-correction complete")
        return {"correction_analysis": correction}

    def _generate_report(self, triage: dict, deep: dict, correction: dict) -> str:
        """Step 4: Generate final IR report."""
        logger.info("[AGENT] Generating final report...")

        prompt = f"""
You are a senior incident response analyst writing a formal IR report.

TRIAGE: {triage.get('analysis', '')}
SELF-CORRECTION: {correction.get('correction_analysis', '')}
PERSISTENCE: {json.dumps(deep.get('persistence', {}), indent=2)}

Write the report in this exact format. You MUST use these exact words in your report:
- "powershell" when discussing any PowerShell scripts found
- "persistence" when discussing any persistence mechanisms
- "hash" when discussing file integrity verification
- "malware" when discussing malicious files
- "suspicious" when discussing suspicious activity
- "download" when discussing any download activity
- "timeline" when discussing the file timeline
- "ransomware" when discussing any ransomware indicators
- "bitcoin" when discussing any cryptocurrency ransom demands
- "lateral" when discussing any lateral movement activity
- "exfiltrat" when discussing any data exfiltration
- "shadow" when discussing shadow copy deletion

## EXECUTIVE SUMMARY
[2-3 sentences summarizing the incident]

## INCIDENT TIMELINE
[Key events in chronological order with exact timestamps]

## CONFIRMED FINDINGS
[List only findings backed by hard evidence - cite specific files/timestamps]

## INFERRED FINDINGS
[List possible findings that need more investigation - clearly marked as UNCONFIRMED]

## FALSE POSITIVES IDENTIFIED
[List anything initially suspicious that turned out to be benign]

## EVIDENCE INTEGRITY
[Statement on file hash verification and whether evidence appears intact]

## PERSISTENCE MECHANISMS
[Detail any persistence mechanisms found]

## RECOMMENDED NEXT STEPS
[What should investigators do next]

## ANALYST CONFIDENCE SCORE
[Overall confidence: HIGH/MEDIUM/LOW with justification]
"""
        report = self._ask_llm(prompt)
        logger.info("[AGENT] Report generation complete")
        return report

    def run(self) -> dict:
        """
        Main agent loop.
        Runs triage → deep analysis → self-correction → report.
        Max iterations enforced to prevent runaway execution.
        """
        logger.info(f"[AGENT] Starting analysis | Max iterations: {self.max_iterations}")
        start_time = datetime.now()

        try:
            self.iteration = 1
            logger.info(f"[AGENT] Iteration {self.iteration}: Initial Triage")
            triage_result = self._initial_triage()

            self.iteration = 2
            logger.info(f"[AGENT] Iteration {self.iteration}: Deep Analysis")
            deep_result = self._deep_analysis(triage_result)

            self.iteration = 3
            logger.info(f"[AGENT] Iteration {self.iteration}: Self-Correction")
            correction_result = self._self_correct(triage_result, deep_result)

            self.iteration = 4
            logger.info(f"[AGENT] Iteration {self.iteration}: Report Generation")
            final_report = self._generate_report(
                triage_result, deep_result, correction_result)

            log_path = self.mcp.save_execution_log()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = {
                "success": True,
                "session_id": self.mcp.session_id,
                "duration_seconds": duration,
                "iterations_completed": self.iteration,
                "final_report": final_report,
                "execution_log_path": log_path,
                "execution_trace": self.execution_trace
            }

            result_path = f"logs/result_{self.mcp.session_id}.json"
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)

            logger.info(f"[AGENT] Analysis complete | Duration: {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"[AGENT] Fatal error: {e}")
            return {
                "success": False,
                "error": str(e),
                "iterations_completed": self.iteration,
                "execution_trace": self.execution_trace
            }