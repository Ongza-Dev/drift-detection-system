"""Tests for drift reporter module."""

import pytest

from drift_detection.reporter import DriftReporter


@pytest.fixture
def reporter():
    """Create reporter instance."""
    return DriftReporter()


def test_report_no_drift(reporter):
    """Test report generation when no drift."""
    drift_result = {
        "environment": "dev",
        "baseline_timestamp": "2024-01-01T00:00:00",
        "current_timestamp": "2024-01-02T00:00:00",
        "drift_detected": False,
        "drift_summary": {"added": [], "removed": [], "changed": []},
        "baseline_resources": {},
        "current_resources": {},
    }

    report = reporter.generate_report(drift_result)

    assert report["drift_detected"] is False
    assert "No drift detected" in report["summary"]
    assert "risk_assessment" in report
    assert report["risk_assessment"]["overall_risk"] == "info"


def test_report_with_drift(reporter):
    """Test report generation with drift."""
    drift_result = {
        "environment": "dev",
        "baseline_timestamp": "2024-01-01T00:00:00",
        "current_timestamp": "2024-01-02T00:00:00",
        "drift_detected": True,
        "drift_summary": {
            "added": ["root['resources']['s3'][0]"],
            "removed": ["root['resources']['ec2'][0]"],
            "changed": ["root['resources']['rds'][0]['db_instance_class']"],
        },
        "baseline_resources": {
            "ec2": [{"instance_type": "t3.micro", "state": "running"}],
            "rds": [],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
        "current_resources": {
            "ec2": [],
            "rds": [{"db_instance_class": "db.t3.micro"}],
            "s3": [{"bucket_name": "new-bucket"}],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
    }

    report = reporter.generate_report(drift_result)

    assert report["drift_detected"] is True
    assert "1 added" in report["summary"]
    assert "Risk:" in report["summary"]
    assert len(report["recommendations"]) > 0
    assert "risk_assessment" in report
    assert "overall_risk" in report["risk_assessment"]
    assert "cost_impact" in report
