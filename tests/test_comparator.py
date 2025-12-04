"""Tests for drift comparator module."""

import pytest

from drift_detection.comparator import DriftComparator


@pytest.fixture
def comparator():
    """Create comparator instance."""
    return DriftComparator()


def test_no_drift_detected(comparator):
    """Test when no drift exists."""
    baseline = {
        "environment": "dev",
        "timestamp": "2024-01-01T00:00:00",
        "resources": {"ec2": [{"instance_id": "i-123", "instance_type": "t3.micro"}]},
    }
    current = {
        "environment": "dev",
        "timestamp": "2024-01-02T00:00:00",
        "resources": {"ec2": [{"instance_id": "i-123", "instance_type": "t3.micro"}]},
    }

    result = comparator.compare(baseline, current)

    assert result["drift_detected"] is False
    assert result["environment"] == "dev"


def test_drift_detected_changed_value(comparator):
    """Test drift detection when value changes."""
    baseline = {
        "environment": "dev",
        "timestamp": "2024-01-01T00:00:00",
        "resources": {"ec2": [{"instance_id": "i-123", "instance_type": "t3.micro"}]},
    }
    current = {
        "environment": "dev",
        "timestamp": "2024-01-02T00:00:00",
        "resources": {"ec2": [{"instance_id": "i-123", "instance_type": "t3.small"}]},
    }

    result = comparator.compare(baseline, current)

    assert result["drift_detected"] is True
    assert len(result["drift_summary"]["changed"]) > 0


def test_drift_detected_added_resource(comparator):
    """Test drift detection when resource is added."""
    baseline = {
        "environment": "dev",
        "timestamp": "2024-01-01T00:00:00",
        "resources": {"ec2": []},
    }
    current = {
        "environment": "dev",
        "timestamp": "2024-01-02T00:00:00",
        "resources": {"ec2": [{"instance_id": "i-123", "instance_type": "t3.micro"}]},
    }

    result = comparator.compare(baseline, current)

    assert result["drift_detected"] is True
