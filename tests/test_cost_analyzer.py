"""Tests for cost analyzer module."""

import pytest

from drift_detection.cost_analyzer import CostAnalyzer


@pytest.fixture
def analyzer():
    """Create analyzer instance."""
    return CostAnalyzer()


def test_no_drift_no_cost_impact(analyzer):
    """Test no cost impact when no drift."""
    drift_result = {"drift_detected": False}

    result = analyzer.analyze_cost_impact(drift_result)

    assert result["total_monthly_impact"] == 0.0


def test_cost_impact_with_added_instance(analyzer):
    """Test cost impact when instance is added."""
    drift_result = {
        "drift_detected": True,
        "baseline_resources": {
            "ec2": [],
            "rds": [],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
        "current_resources": {
            "ec2": [{"instance_type": "t3.micro", "state": "running"}],
            "rds": [],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
    }

    result = analyzer.analyze_cost_impact(drift_result)

    assert result["monthly_impact"] > 0
    assert result["current_monthly_cost"] > result["baseline_monthly_cost"]


def test_cost_calculation_multiple_resources(analyzer):
    """Test cost calculation with multiple resources."""
    drift_result = {
        "drift_detected": True,
        "baseline_resources": {
            "ec2": [{"instance_type": "t3.micro", "state": "running"}],
            "rds": [],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
        "current_resources": {
            "ec2": [
                {"instance_type": "t3.micro", "state": "running"},
                {"instance_type": "t3.small", "state": "running"},
            ],
            "rds": [{"db_instance_class": "db.t3.micro"}],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        },
    }

    result = analyzer.analyze_cost_impact(drift_result)

    assert result["monthly_impact"] > 0
    assert "impact_percentage" in result
