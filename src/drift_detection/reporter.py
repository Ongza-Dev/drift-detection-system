"""Report generation for drift detection results."""

import logging
from typing import Any, Dict, List

from drift_detection.cost_analyzer import CostAnalyzer
from drift_detection.risk_scorer import RiskScorer

logger = logging.getLogger(__name__)


class DriftReporter:
    """Generates drift detection reports."""

    def __init__(self):
        self.cost_analyzer = CostAnalyzer()
        self.risk_scorer = RiskScorer()

    def generate_report(self, drift_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive drift report."""
        logger.info(f"Generating report for {drift_result['environment']}")

        cost_impact = self.cost_analyzer.analyze_cost_impact(drift_result)
        risk_assessment = self.risk_scorer.score_drift(drift_result)

        report = {
            "environment": drift_result["environment"],
            "baseline_timestamp": drift_result["baseline_timestamp"],
            "current_timestamp": drift_result["current_timestamp"],
            "drift_detected": drift_result["drift_detected"],
            "summary": self._create_summary(drift_result, risk_assessment),
            "details": drift_result["drift_summary"],
            "risk_assessment": risk_assessment,
            "cost_impact": cost_impact,
            "recommendations": self._generate_recommendations(
                drift_result, risk_assessment
            ),
        }

        return report

    def _create_summary(
        self, drift_result: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> str:
        """Create summary text."""
        if not drift_result["drift_detected"]:
            return "No drift detected. Infrastructure matches baseline."

        summary = drift_result["drift_summary"]
        added = len(summary["added"])
        removed = len(summary["removed"])
        changed = len(summary["changed"])
        risk = risk_assessment["overall_risk"].upper()

        return (
            f"Drift detected: {added} added, {removed} removed, "
            f"{changed} changed. Risk: {risk}"
        )

    def _generate_recommendations(
        self, drift_result: Dict[str, Any], risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        if not drift_result["drift_detected"]:
            return ["Continue monitoring for drift."]

        recommendations = []
        risk = risk_assessment["overall_risk"]

        if risk == "critical":
            recommendations.append(
                "⚠️  CRITICAL: Immediate action required - review all changes"
            )
        elif risk == "high":
            recommendations.append("⚠️  HIGH RISK: Review changes within 24 hours")

        summary = drift_result["drift_summary"]
        if summary["removed"]:
            recommendations.append(
                "Investigate removed resources - potential data loss risk"
            )
        if summary["added"]:
            recommendations.append(
                "Verify added resources are authorized and properly tagged"
            )
        if summary["changed"]:
            recommendations.append(
                "Review configuration changes for security implications"
            )

        recommendations.append("Update baseline if changes are intentional")

        return recommendations
