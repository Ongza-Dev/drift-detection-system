"""Risk scoring for infrastructure drift."""

import logging
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RiskScorer:
    """Scores risk level of infrastructure drift."""

    # Risk weights by resource type
    RESOURCE_RISK = {
        "vpc": RiskLevel.HIGH,
        "ec2": RiskLevel.HIGH,
        "rds": RiskLevel.CRITICAL,
        "s3": RiskLevel.MEDIUM,
        "lambda": RiskLevel.MEDIUM,
        "ecs": RiskLevel.HIGH,
    }

    # Risk weights by change type
    CHANGE_RISK = {
        "removed": RiskLevel.CRITICAL,
        "added": RiskLevel.MEDIUM,
        "changed": RiskLevel.MEDIUM,
    }

    # Critical fields that elevate risk
    CRITICAL_FIELDS = {
        "instance_type",
        "db_instance_class",
        "cidr_block",
        "state",
        "engine",
        "runtime",
        "desired_count",
        "memory_size",
    }

    def score_drift(self, drift_result: Dict[str, Any]) -> Dict[str, Any]:
        """Score risk for all detected drift."""
        if not drift_result["drift_detected"]:
            return {"overall_risk": RiskLevel.INFO, "scored_changes": []}

        scored_changes = []
        risk_levels = []

        for change_type in ["added", "removed", "changed"]:
            for item in drift_result["drift_summary"].get(change_type, []):
                score = self._score_change(item, change_type)
                scored_changes.append(score)
                risk_levels.append(score["risk_level"])

        overall_risk = self._calculate_overall_risk(risk_levels)

        return {
            "overall_risk": overall_risk,
            "scored_changes": scored_changes,
            "risk_distribution": self._count_by_risk(risk_levels),
        }

    def _score_change(self, change_path: str, change_type: str) -> Dict[str, Any]:
        """Score individual change."""
        resource_type = self._extract_resource_type(change_path)
        field_name = self._extract_field_name(change_path)

        base_risk = self.RESOURCE_RISK.get(resource_type, RiskLevel.LOW)
        change_risk = self.CHANGE_RISK.get(change_type, RiskLevel.LOW)

        # Start with higher of base or change risk
        final_risk = self._max_risk(base_risk, change_risk)

        # Elevate risk if critical field changed
        if field_name in self.CRITICAL_FIELDS:
            final_risk = self._elevate_risk(final_risk)

        return {
            "change_path": change_path,
            "change_type": change_type,
            "resource_type": resource_type,
            "field_name": field_name,
            "risk_level": final_risk,
            "reason": self._get_risk_reason(resource_type, change_type, field_name),
        }

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from change path."""
        if "['vpc']" in path:
            return "vpc"
        elif "['ec2']" in path:
            return "ec2"
        elif "['rds']" in path:
            return "rds"
        elif "['s3']" in path:
            return "s3"
        elif "['lambda']" in path:
            return "lambda"
        elif "['ecs']" in path:
            return "ecs"
        return "unknown"

    def _extract_field_name(self, path: str) -> str:
        """Extract field name from change path."""
        parts = path.split("'")
        if len(parts) >= 4:
            return parts[-2]
        return "unknown"

    def _max_risk(self, risk1: RiskLevel, risk2: RiskLevel) -> RiskLevel:
        """Return the higher risk level."""
        order = [
            RiskLevel.INFO,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]
        idx1 = order.index(risk1) if risk1 in order else 0
        idx2 = order.index(risk2) if risk2 in order else 0
        return order[max(idx1, idx2)]

    def _elevate_risk(self, risk: RiskLevel) -> RiskLevel:
        """Elevate risk by one level."""
        elevation = {
            RiskLevel.INFO: RiskLevel.LOW,
            RiskLevel.LOW: RiskLevel.MEDIUM,
            RiskLevel.MEDIUM: RiskLevel.HIGH,
            RiskLevel.HIGH: RiskLevel.CRITICAL,
            RiskLevel.CRITICAL: RiskLevel.CRITICAL,
        }
        return elevation.get(risk, risk)

    def _calculate_overall_risk(self, risk_levels: List[RiskLevel]) -> RiskLevel:
        """Calculate overall risk from individual risks."""
        if not risk_levels:
            return RiskLevel.INFO

        order = [
            RiskLevel.INFO,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]
        max_risk = RiskLevel.INFO
        for risk in risk_levels:
            if risk in order and order.index(risk) > order.index(max_risk):
                max_risk = risk
        return max_risk

    def _count_by_risk(self, risk_levels: List[RiskLevel]) -> Dict[str, int]:
        """Count changes by risk level."""
        counts = {level.value: 0 for level in RiskLevel}
        for level in risk_levels:
            counts[level.value] += 1
        return counts

    def _get_risk_reason(
        self, resource_type: str, change_type: str, field_name: str
    ) -> str:
        """Generate human-readable risk reason."""
        reasons = {
            "rds": "Database changes can cause downtime or data loss",
            "vpc": "Network changes can break connectivity",
            "ec2": "Compute changes affect performance and cost",
            "ecs": "Container changes can disrupt services",
            "lambda": "Function changes may break integrations",
            "s3": "Storage changes can affect data access",
        }

        base_reason = reasons.get(resource_type, "Infrastructure change detected")

        if change_type == "removed":
            return f"{base_reason} - Resource removed"
        elif field_name in self.CRITICAL_FIELDS:
            return f"{base_reason} - Critical field '{field_name}' modified"

        return base_reason
