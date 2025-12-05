"""Tests for CLI module."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from drift_detection.cli import cli


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_components():
    """Mock all components."""
    with patch("drift_detection.cli.AWSScanner") as mock_scanner, patch(
        "drift_detection.cli.S3Storage"
    ) as mock_storage, patch("drift_detection.cli.DriftComparator") as mock_comparator, patch(
        "drift_detection.cli.DriftReporter"
    ) as mock_reporter, patch(
        "drift_detection.cli.SNSNotifier"
    ) as mock_notifier:
        yield {
            "scanner": mock_scanner,
            "storage": mock_storage,
            "comparator": mock_comparator,
            "reporter": mock_reporter,
            "notifier": mock_notifier,
        }


def test_scan_command(runner, mock_components):
    """Test scan command."""
    mock_storage = mock_components["storage"].return_value
    mock_scanner = mock_components["scanner"].return_value

    mock_scanner.scan_environment.return_value = {"environment": "dev"}
    mock_storage.save_scan.return_value = "scans/dev/test.json"

    result = runner.invoke(cli, ["--bucket", "test-bucket", "scan", "dev"])

    assert result.exit_code == 0
    assert "Scan completed" in result.output


def test_baseline_command(runner, mock_components):
    """Test baseline command."""
    mock_storage = mock_components["storage"].return_value
    mock_scanner = mock_components["scanner"].return_value

    mock_scanner.scan_environment.return_value = {"environment": "dev"}
    mock_storage.save_baseline.return_value = "baselines/dev/baseline.json"

    result = runner.invoke(cli, ["--bucket", "test-bucket", "baseline", "dev"])

    assert result.exit_code == 0
    assert "Baseline created" in result.output


def test_detect_no_baseline(runner, mock_components):
    """Test detect command when no baseline exists."""
    mock_storage = mock_components["storage"].return_value
    mock_storage.load_baseline.return_value = None

    result = runner.invoke(cli, ["--bucket", "test-bucket", "detect", "dev"])

    assert result.exit_code == 1
    assert "No baseline found" in result.output


def test_detect_no_drift(runner, mock_components):
    """Test detect command with no drift."""
    mock_storage = mock_components["storage"].return_value
    mock_scanner = mock_components["scanner"].return_value
    mock_comparator = mock_components["comparator"].return_value
    mock_reporter = mock_components["reporter"].return_value

    mock_storage.load_baseline.return_value = {"environment": "dev"}
    mock_scanner.scan_environment.return_value = {"environment": "dev"}
    mock_comparator.compare.return_value = {"drift_detected": False}
    mock_reporter.generate_report.return_value = {
        "drift_detected": False,
        "summary": "No drift",
    }
    mock_storage.save_report.return_value = "reports/dev/test.json"

    result = runner.invoke(cli, ["--bucket", "test-bucket", "detect", "dev"])

    assert result.exit_code == 0
    assert "No drift detected" in result.output


def test_detect_with_drift(runner, mock_components):
    """Test detect command with drift detected."""
    mock_storage = mock_components["storage"].return_value
    mock_scanner = mock_components["scanner"].return_value
    mock_comparator = mock_components["comparator"].return_value
    mock_reporter = mock_components["reporter"].return_value

    mock_storage.load_baseline.return_value = {"environment": "dev"}
    mock_scanner.scan_environment.return_value = {"environment": "dev"}
    mock_comparator.compare.return_value = {"drift_detected": True}
    mock_reporter.generate_report.return_value = {
        "drift_detected": True,
        "summary": "Drift detected: 1 added, 0 removed, 1 changed. Risk: HIGH",
        "risk_assessment": {
            "overall_risk": "high",
            "risk_distribution": {"high": 1, "medium": 0, "low": 0},
        },
        "cost_impact": {"monthly_impact": 50.0, "impact_percentage": 100.0},
        "recommendations": ["Review changes"],
    }
    mock_storage.save_report.return_value = "reports/dev/test.json"

    result = runner.invoke(cli, ["--bucket", "test-bucket", "detect", "dev"])

    assert result.exit_code == 0
    assert "Drift detected" in result.output


def test_detect_with_sns(runner, mock_components):
    """Test detect command with SNS alerting."""
    mock_storage = mock_components["storage"].return_value
    mock_scanner = mock_components["scanner"].return_value
    mock_comparator = mock_components["comparator"].return_value
    mock_reporter = mock_components["reporter"].return_value
    mock_notifier = mock_components["notifier"].return_value

    mock_storage.load_baseline.return_value = {"environment": "dev"}
    mock_scanner.scan_environment.return_value = {"environment": "dev"}
    mock_comparator.compare.return_value = {"drift_detected": True}
    mock_reporter.generate_report.return_value = {
        "drift_detected": True,
        "summary": "Drift detected",
        "risk_assessment": {
            "overall_risk": "high",
            "risk_distribution": {"high": 1},
        },
        "cost_impact": {"monthly_impact": 50.0, "impact_percentage": 100.0},
        "recommendations": ["Review"],
    }
    mock_storage.save_report.return_value = "reports/dev/test.json"
    mock_notifier.return_value.send_alert.return_value = "msg-123"

    result = runner.invoke(
        cli,
        [
            "--bucket",
            "test-bucket",
            "--sns-topic",
            "arn:aws:sns:us-east-1:123:topic",
            "detect",
            "dev",
        ],
    )

    assert result.exit_code == 0
    assert "Alert sent" in result.output
