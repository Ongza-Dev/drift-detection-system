"""Tests for SNS notifier module."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from drift_detection.notifier import SNSNotifier


@pytest.fixture
def notifier():
    """Create notifier instance."""
    with patch("drift_detection.notifier.boto3"):
        return SNSNotifier(region="us-east-1")


@pytest.fixture
def drift_report():
    """Sample drift report."""
    return {
        "environment": "prod",
        "risk_assessment": {
            "overall_risk": "high",
            "risk_distribution": {"critical": 0, "high": 1, "medium": 1},
        },
        "summary": "Drift detected: 1 added, 0 removed, 1 changed. Risk: HIGH",
        "cost_impact": {"monthly_impact": 50.0, "impact_percentage": 100.0},
        "recommendations": ["Review changes", "Update baseline"],
    }


def test_send_alert_high_risk(notifier, drift_report):
    """Test sending alert for high risk drift."""
    notifier.sns.publish = MagicMock(return_value={"MessageId": "msg-123"})

    message_id = notifier.send_alert(
        drift_report, "arn:aws:sns:us-east-1:123:topic", min_risk="high"
    )

    assert message_id == "msg-123"
    notifier.sns.publish.assert_called_once()


def test_send_alert_below_threshold(notifier):
    """Test alert not sent when below risk threshold."""
    report = {
        "environment": "dev",
        "risk_assessment": {"overall_risk": "low"},
        "summary": "Low risk drift",
        "cost_impact": {"monthly_impact": 0},
        "recommendations": [],
    }

    message_id = notifier.send_alert(
        report, "arn:aws:sns:us-east-1:123:topic", min_risk="high"
    )

    assert message_id is None


def test_send_alert_critical_risk(notifier):
    """Test sending alert for critical risk."""
    report = {
        "environment": "prod",
        "risk_assessment": {
            "overall_risk": "critical",
            "risk_distribution": {"critical": 1},
        },
        "summary": "Critical drift",
        "cost_impact": {"monthly_impact": 100.0, "impact_percentage": 200.0},
        "recommendations": ["Immediate action required"],
    }

    notifier.sns.publish = MagicMock(return_value={"MessageId": "msg-456"})

    message_id = notifier.send_alert(
        report, "arn:aws:sns:us-east-1:123:topic", min_risk="high"
    )

    assert message_id == "msg-456"


def test_send_alert_sns_error(notifier, drift_report):
    """Test handling SNS publish error."""
    notifier.sns.publish = MagicMock(
        side_effect=ClientError({"Error": {"Code": "500"}}, "Publish")
    )

    message_id = notifier.send_alert(
        drift_report, "arn:aws:sns:us-east-1:123:topic", min_risk="high"
    )

    assert message_id is None


def test_format_subject(notifier, drift_report):
    """Test subject formatting."""
    subject = notifier._format_subject(drift_report)

    assert "HIGH" in subject
    assert "prod" in subject


def test_format_message(notifier, drift_report):
    """Test message formatting."""
    message = notifier._format_message(drift_report)

    assert "prod" in message
    assert "HIGH" in message
    assert "50.0" in message
    assert "Review changes" in message
