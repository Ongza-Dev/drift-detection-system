"""Tests for S3 storage module."""

import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from drift_detection.storage import S3Storage


@pytest.fixture
def mock_s3_client():
    """Mock S3 client."""
    with patch("drift_detection.storage.boto3.client") as mock:
        yield mock.return_value


def test_save_baseline(mock_s3_client):
    """Test saving baseline to S3."""
    storage = S3Storage(bucket_name="test-bucket")
    data = {"environment": "dev", "resources": {}}

    key = storage.save_baseline("dev", data)

    assert key == "baselines/dev/baseline.json"
    mock_s3_client.put_object.assert_called_once()


def test_load_baseline_success(mock_s3_client):
    """Test loading baseline from S3."""
    storage = S3Storage(bucket_name="test-bucket")
    test_data = {"environment": "dev", "resources": {}}

    mock_s3_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: json.dumps(test_data).encode())
    }

    result = storage.load_baseline("dev")

    assert result == test_data


def test_load_baseline_not_found(mock_s3_client):
    """Test loading non-existent baseline."""
    storage = S3Storage(bucket_name="test-bucket")

    error = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
    )
    mock_s3_client.get_object.side_effect = error

    result = storage.load_baseline("dev")

    assert result is None
