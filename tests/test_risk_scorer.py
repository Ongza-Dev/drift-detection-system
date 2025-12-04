"""Tests for risk scoring module."""

import unittest

from drift_detection.risk_scorer import RiskLevel, RiskScorer


class TestRiskScorer(unittest.TestCase):
    """Test risk scoring functionality."""

    def setUp(self):
        self.scorer = RiskScorer()

    def test_no_drift_returns_info_risk(self):
        """Test that no drift returns INFO risk level."""
        drift_result = {
            "drift_detected": False,
            "drift_summary": {"added": [], "removed": [], "changed": []},
        }

        result = self.scorer.score_drift(drift_result)

        self.assertEqual(result["overall_risk"], RiskLevel.INFO)
        self.assertEqual(len(result["scored_changes"]), 0)

    def test_removed_rds_is_critical(self):
        """Test that removed RDS resource is CRITICAL risk."""
        drift_result = {
            "drift_detected": True,
            "drift_summary": {
                "added": [],
                "removed": ["root['resources']['rds'][0]"],
                "changed": [],
            },
        }

        result = self.scorer.score_drift(drift_result)

        self.assertEqual(result["overall_risk"], RiskLevel.CRITICAL)
        self.assertEqual(len(result["scored_changes"]), 1)
        self.assertEqual(result["scored_changes"][0]["risk_level"], RiskLevel.CRITICAL)

    def test_changed_ec2_instance_type_is_high_risk(self):
        """Test that changed EC2 instance type is HIGH risk."""
        drift_result = {
            "drift_detected": True,
            "drift_summary": {
                "added": [],
                "removed": [],
                "changed": ["root['resources']['ec2'][0]['instance_type']"],
            },
        }

        result = self.scorer.score_drift(drift_result)

        # EC2 is HIGH base risk, instance_type is critical field -> elevated to CRITICAL
        self.assertEqual(result["overall_risk"], RiskLevel.CRITICAL)

    def test_added_s3_bucket_is_medium_risk(self):
        """Test that added S3 bucket is MEDIUM risk."""
        drift_result = {
            "drift_detected": True,
            "drift_summary": {
                "added": ["root['resources']['s3'][0]"],
                "removed": [],
                "changed": [],
            },
        }

        result = self.scorer.score_drift(drift_result)

        self.assertEqual(result["overall_risk"], RiskLevel.MEDIUM)

    def test_risk_distribution_counts(self):
        """Test risk distribution counting."""
        drift_result = {
            "drift_detected": True,
            "drift_summary": {
                "added": ["root['resources']['s3'][0]"],
                "removed": ["root['resources']['rds'][0]"],
                "changed": ["root['resources']['ec2'][0]['instance_type']"],
            },
        }

        result = self.scorer.score_drift(drift_result)

        self.assertGreater(result["risk_distribution"]["critical"], 0)
        self.assertIn("risk_distribution", result)

    def test_extract_resource_type(self):
        """Test resource type extraction from path."""
        self.assertEqual(
            self.scorer._extract_resource_type("root['resources']['vpc'][0]"), "vpc"
        )
        self.assertEqual(
            self.scorer._extract_resource_type("root['resources']['ec2'][0]"), "ec2"
        )
        self.assertEqual(
            self.scorer._extract_resource_type("root['resources']['rds'][0]"), "rds"
        )

    def test_extract_field_name(self):
        """Test field name extraction from path."""
        path = "root['resources']['ec2'][0]['instance_type']"
        self.assertEqual(self.scorer._extract_field_name(path), "instance_type")

    def test_multiple_changes_highest_risk_wins(self):
        """Test that overall risk is highest individual risk."""
        drift_result = {
            "drift_detected": True,
            "drift_summary": {
                "added": ["root['resources']['s3'][0]"],  # MEDIUM
                "removed": [],
                "changed": [
                    "root['resources']['lambda'][0]['runtime']"
                ],  # MEDIUM->HIGH
            },
        }

        result = self.scorer.score_drift(drift_result)

        # Should be HIGH (elevated from MEDIUM due to critical field)
        self.assertIn(result["overall_risk"], [RiskLevel.HIGH, RiskLevel.CRITICAL])


if __name__ == "__main__":
    unittest.main()
