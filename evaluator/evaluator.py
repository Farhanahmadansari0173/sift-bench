# evaluator/evaluator.py
# SIFT-BENCH: Ground Truth Evaluator
# Compares agent findings vs known ground truth
# This is what makes our project unique - we MEASURE accuracy

import json
import os
from datetime import datetime
from loguru import logger

class Evaluator:
    """
    Evaluates IR Agent accuracy against known ground truth.
    Calculates true positives, false positives, hallucinations.
    This is the core differentiator of SIFT-BENCH.
    """

    def __init__(self, ground_truth_path: str):
        self.ground_truth_path = ground_truth_path
        self.ground_truth = self._load_ground_truth()
        logger.info(f"Evaluator initialized | Ground truth: {ground_truth_path}")

    def _load_ground_truth(self) -> dict:
        """Load ground truth file."""
        try:
            with open(self.ground_truth_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load ground truth: {e}")
            return {}

    def evaluate(self, agent_result: dict) -> dict:
        """
        Compare agent findings against ground truth.
        Returns accuracy scores.
        """
        logger.info("[EVALUATOR] Starting evaluation...")

        report_text = agent_result.get("final_report", "").lower()
        ground_truth = self.ground_truth

        # Check which ground truth items were found
        true_positives = []
        false_negatives = []

        expected_findings = ground_truth.get("expected_findings", [])
        for finding in expected_findings:
            keyword = finding["keyword"].lower()
            if keyword in report_text:
                true_positives.append(finding)
            else:
                false_negatives.append(finding)

        # Check for hallucinations
        hallucinations = []
        forbidden_claims = ground_truth.get("forbidden_claims", [])
        for claim in forbidden_claims:
            if claim["keyword"].lower() in report_text:
                hallucinations.append(claim)

        # Calculate scores
        total_expected = len(expected_findings)
        tp = len(true_positives)
        fn = len(false_negatives)
        hall = len(hallucinations)

        accuracy = (tp / total_expected * 100) if total_expected > 0 else 0
        hallucination_rate = (hall / max(tp + hall, 1)) * 100

        result = {
            "timestamp": datetime.now().isoformat(),
            "accuracy_score": round(accuracy, 2),
            "hallucination_rate": round(hallucination_rate, 2),
            "true_positives": tp,
            "false_negatives": fn,
            "hallucinations": hall,
            "true_positive_details": true_positives,
            "false_negative_details": false_negatives,
            "hallucination_details": hallucinations,
            "total_expected_findings": total_expected,
            "grade": self._grade(accuracy, hallucination_rate)
        }

        logger.info(f"[EVALUATOR] Accuracy: {accuracy:.1f}% | "
                   f"Hallucination rate: {hallucination_rate:.1f}%")
        return result

    def _grade(self, accuracy: float, hallucination_rate: float) -> str:
        """Grade the agent performance."""
        if accuracy >= 80 and hallucination_rate < 10:
            return "EXCELLENT"
        elif accuracy >= 60 and hallucination_rate < 20:
            return "GOOD"
        elif accuracy >= 40:
            return "FAIR"
        else:
            return "NEEDS_IMPROVEMENT"

    def compare_iterations(self, results: list) -> dict:
        """
        Compare accuracy across multiple iterations.
        Shows improvement over time - key demo point for judges.
        """
        if not results:
            return {}

        comparison = {
            "iterations": len(results),
            "accuracy_progression": [r.get("accuracy_score", 0) for r in results],
            "hallucination_progression": [r.get("hallucination_rate", 0) for r in results],
            "improved": False,
            "improvement_delta": 0
        }

        if len(results) >= 2:
            first = results[0].get("accuracy_score", 0)
            last = results[-1].get("accuracy_score", 0)
            comparison["improved"] = last > first
            comparison["improvement_delta"] = round(last - first, 2)

        return comparison