"""Drift detection and comparison logic."""

import logging
from typing import Any, Dict, List

from deepdiff import DeepDiff

logger = logging.getLogger(__name__)


class DriftComparator:
    """Compares infrastructure configurations to detect drift."""

    def compare(
        self, baseline: Dict[str, Any], current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare baseline and current configurations."""
        logger.info(f"Comparing {baseline['environment']} baseline with current state")

        diff = DeepDiff(
            baseline["resources"],
            current["resources"],
            ignore_order=True,
            report_repetition=True,
        )

        drift_detected = len(diff) > 0
        drift_summary = self._summarize_drift(diff)

        return {
            "environment": current["environment"],
            "baseline_timestamp": baseline["timestamp"],
            "current_timestamp": current["timestamp"],
            "drift_detected": drift_detected,
            "drift_summary": drift_summary,
            "detailed_diff": diff.to_dict() if drift_detected else {},
            "baseline_resources": baseline["resources"],
            "current_resources": current["resources"],
        }

    def _summarize_drift(self, diff: DeepDiff) -> Dict[str, List[str]]:
        """Create human-readable drift summary."""
        summary: Dict[str, List[str]] = {
            "added": [],
            "removed": [],
            "changed": [],
        }

        if "dictionary_item_added" in diff:
            for item in diff["dictionary_item_added"]:
                summary["added"].append(str(item))

        if "dictionary_item_removed" in diff:
            for item in diff["dictionary_item_removed"]:
                summary["removed"].append(str(item))

        if "values_changed" in diff:
            for item in diff["values_changed"]:
                summary["changed"].append(str(item))

        return summary
