"""S3 storage operations for drift detection data."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Storage:
    """Handles S3 storage operations for baselines, scans, and reports."""

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.s3 = boto3.client("s3", region_name=region)

    def save_baseline(self, environment: str, data: Dict[str, Any]) -> str:
        """Save baseline configuration for an environment."""
        key = f"baselines/{environment}/baseline.json"
        return self._save_json(key, data)

    def load_baseline(self, environment: str) -> Optional[Dict[str, Any]]:
        """Load baseline configuration for an environment."""
        key = f"baselines/{environment}/baseline.json"
        return self._load_json(key)

    def save_scan(self, environment: str, data: Dict[str, Any]) -> str:
        """Save scan results with timestamp."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        key = f"scans/{environment}/{timestamp}.json"
        return self._save_json(key, data)

    def save_report(self, environment: str, data: Dict[str, Any]) -> str:
        """Save drift report with timestamp."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        key = f"reports/{environment}/{timestamp}.json"
        return self._save_json(key, data)

    def _save_json(self, key: str, data: Dict[str, Any]) -> str:
        """Save JSON data to S3."""
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType="application/json",
            )
            logger.info(f"Saved to s3://{self.bucket_name}/{key}")
            return key
        except ClientError as e:
            logger.error(f"Failed to save {key}: {e}")
            raise

    def _load_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from S3."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(response["Body"].read())
            logger.info(f"Loaded from s3://{self.bucket_name}/{key}")
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"Key not found: {key}")
                return None
            logger.error(f"Failed to load {key}: {e}")
            raise
