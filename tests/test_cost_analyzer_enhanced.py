"""Tests for enhanced cost analyzer with all resource types."""

import unittest

from drift_detection.cost_analyzer import CostAnalyzer


class TestEnhancedCostAnalyzer(unittest.TestCase):
    """Test enhanced cost analysis for all resource types."""

    def setUp(self):
        self.analyzer = CostAnalyzer()

    def test_s3_cost_calculation(self):
        """Test S3 storage cost calculation."""
        baseline = {
            "resources": {
                "s3": [],
                "ec2": [],
                "rds": [],
                "lambda": [],
                "ecs": [],
                "vpc": [],
            }
        }
        current = {
            "resources": {
                "s3": [{"bucket_name": "test-bucket"}],
                "ec2": [],
                "rds": [],
                "lambda": [],
                "ecs": [],
                "vpc": [],
            }
        }

        baseline_cost = self.analyzer._calculate_environment_cost(baseline["resources"])
        current_cost = self.analyzer._calculate_environment_cost(current["resources"])

        self.assertEqual(baseline_cost, 0.0)
        self.assertGreater(current_cost, 0.0)

    def test_lambda_cost_calculation(self):
        """Test Lambda function cost calculation."""
        resources = {
            "lambda": [{"function_name": "test-func", "memory_size": 1024}],
            "ec2": [],
            "rds": [],
            "s3": [],
            "ecs": [],
            "vpc": [],
        }

        cost = self.analyzer._calculate_environment_cost(resources)
        self.assertGreater(cost, 0.0)

    def test_ecs_cost_calculation(self):
        """Test ECS Fargate cost calculation."""
        resources = {
            "ecs": [{"service_name": "test-service", "desired_count": 2}],
            "ec2": [],
            "rds": [],
            "s3": [],
            "lambda": [],
            "vpc": [],
        }

        cost = self.analyzer._calculate_environment_cost(resources)
        self.assertGreater(cost, 0.0)

    def test_stopped_ec2_not_counted(self):
        """Test that stopped EC2 instances are not counted."""
        resources = {
            "ec2": [
                {"instance_type": "t3.micro", "state": "stopped"},
                {"instance_type": "t3.micro", "state": "running"},
            ],
            "rds": [],
            "s3": [],
            "lambda": [],
            "ecs": [],
            "vpc": [],
        }

        cost = self.analyzer._calculate_environment_cost(resources)
        # Should only count running instance
        self.assertAlmostEqual(cost, 0.0104, places=4)

    def test_comprehensive_cost_impact(self):
        """Test cost impact with multiple resource types."""
        baseline = {
            "resources": {
                "ec2": [{"instance_type": "t3.micro", "state": "running"}],
                "rds": [{"db_instance_class": "db.t3.micro"}],
                "s3": [],
                "lambda": [],
                "ecs": [],
                "vpc": [],
            }
        }
        current = {
            "resources": {
                "ec2": [{"instance_type": "t3.large", "state": "running"}],
                "rds": [{"db_instance_class": "db.t3.micro"}],
                "s3": [{"bucket_name": "new-bucket"}],
                "lambda": [{"function_name": "func", "memory_size": 512}],
                "ecs": [],
                "vpc": [],
            }
        }

        drift_result = {
            "drift_detected": True,
            "baseline_resources": baseline["resources"],
            "current_resources": current["resources"],
        }

        result = self.analyzer.analyze_cost_impact(drift_result)

        self.assertIn("baseline_monthly_cost", result)
        self.assertIn("current_monthly_cost", result)
        self.assertIn("monthly_impact", result)
        self.assertIn("impact_percentage", result)
        self.assertGreater(
            result["current_monthly_cost"], result["baseline_monthly_cost"]
        )

    def test_cost_decrease_shows_negative_impact(self):
        """Test that cost decreases show negative impact."""
        baseline = {
            "resources": {
                "ec2": [{"instance_type": "t3.xlarge", "state": "running"}],
                "rds": [],
                "s3": [],
                "lambda": [],
                "ecs": [],
                "vpc": [],
            }
        }
        current = {
            "resources": {
                "ec2": [{"instance_type": "t3.micro", "state": "running"}],
                "rds": [],
                "s3": [],
                "lambda": [],
                "ecs": [],
                "vpc": [],
            }
        }

        drift_result = {
            "drift_detected": True,
            "baseline_resources": baseline["resources"],
            "current_resources": current["resources"],
        }

        result = self.analyzer.analyze_cost_impact(drift_result)

        self.assertLess(result["monthly_impact"], 0)
        self.assertLess(result["impact_percentage"], 0)


if __name__ == "__main__":
    unittest.main()
