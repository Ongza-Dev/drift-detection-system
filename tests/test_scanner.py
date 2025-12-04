"""Tests for AWS scanner module."""

from unittest.mock import MagicMock, patch

import pytest

from drift_detection.scanner import AWSScanner


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session."""
    with patch("drift_detection.scanner.boto3.Session") as mock:
        yield mock


def test_scanner_initialization(mock_boto3_session):
    """Test scanner initializes with correct region."""
    scanner = AWSScanner(region="us-west-2")
    assert scanner.region == "us-west-2"
    mock_boto3_session.assert_called_once_with(region_name="us-west-2")


def test_scan_environment_structure(mock_boto3_session):
    """Test scan returns correct structure."""
    scanner = AWSScanner()
    scanner.ec2 = MagicMock()
    scanner.rds = MagicMock()
    scanner.s3 = MagicMock()
    scanner.lambda_client = MagicMock()
    scanner.ecs = MagicMock()

    scanner.ec2.describe_vpcs.return_value = {"Vpcs": []}
    scanner.ec2.describe_instances.return_value = {"Reservations": []}
    scanner.rds.describe_db_instances.return_value = {"DBInstances": []}
    scanner.s3.list_buckets.return_value = {"Buckets": []}
    scanner.lambda_client.list_functions.return_value = {"Functions": []}
    scanner.ecs.list_clusters.return_value = {"clusterArns": []}

    result = scanner.scan_environment("dev")

    assert result["environment"] == "dev"
    assert "timestamp" in result
    assert "resources" in result
    assert "vpc" in result["resources"]
    assert "ec2" in result["resources"]
