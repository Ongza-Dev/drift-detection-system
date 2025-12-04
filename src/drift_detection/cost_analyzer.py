"""Cost impact analysis for infrastructure drift."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

COST_PER_HOUR = {
    "ec2": {
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "t3.medium": 0.0416,
        "t3.large": 0.0832,
        "t3.xlarge": 0.1664,
        "t3.2xlarge": 0.3328,
    },
    "rds": {
        "db.t3.micro": 0.017,
        "db.t3.small": 0.034,
        "db.t3.medium": 0.068,
        "db.t3.large": 0.136,
        "db.t3.xlarge": 0.272,
    },
    "nat_gateway": 0.045,
    "load_balancer": 0.0225,
    "s3_storage_gb": 0.023 / 730,  # $0.023/GB/month
    "lambda_gb_second": 0.0000166667,  # Per GB-second
    "ecs_fargate_vcpu": 0.04048,  # Per vCPU per hour
    "ecs_fargate_gb": 0.004445,  # Per GB per hour
}

# Lambda memory to GB conversion
LAMBDA_MEMORY_TO_GB = {
    128: 0.125,
    256: 0.25,
    512: 0.5,
    1024: 1.0,
    2048: 2.0,
    3008: 3.0,
}

# ECS Fargate task sizes (vCPU, memory GB)
ECS_TASK_SIZES = {
    "0.25vCPU-0.5GB": (0.25, 0.5),
    "0.25vCPU-1GB": (0.25, 1.0),
    "0.5vCPU-1GB": (0.5, 1.0),
    "1vCPU-2GB": (1.0, 2.0),
    "2vCPU-4GB": (2.0, 4.0),
}


class CostAnalyzer:
    """Analyzes cost impact of infrastructure drift."""

    def analyze_cost_impact(self, drift_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost impact of drift."""
        if not drift_result["drift_detected"]:
            return {"total_monthly_impact": 0.0, "details": []}

        baseline_cost = self._calculate_environment_cost(
            drift_result.get("baseline_resources", {})
        )
        current_cost = self._calculate_environment_cost(
            drift_result.get("current_resources", {})
        )

        monthly_impact = (current_cost - baseline_cost) * 730

        return {
            "baseline_monthly_cost": round(baseline_cost * 730, 2),
            "current_monthly_cost": round(current_cost * 730, 2),
            "monthly_impact": round(monthly_impact, 2),
            "impact_percentage": round(
                (
                    (monthly_impact / (baseline_cost * 730) * 100)
                    if baseline_cost > 0
                    else 0
                ),
                2,
            ),
        }

    def _calculate_environment_cost(self, resources: Dict[str, Any]) -> float:
        """Calculate hourly cost for environment resources."""
        total_cost = 0.0

        # EC2 instances
        for instance in resources.get("ec2", []):
            instance_type = instance.get("instance_type", "")
            if instance.get("state") == "running":
                cost = COST_PER_HOUR["ec2"].get(instance_type, 0)
                total_cost += cost

        # RDS instances
        for db in resources.get("rds", []):
            instance_class = db.get("db_instance_class", "")
            cost = COST_PER_HOUR["rds"].get(instance_class, 0)
            total_cost += cost

        # S3 buckets (estimate 10GB per bucket)
        s3_count = len(resources.get("s3", []))
        total_cost += s3_count * 10 * COST_PER_HOUR["s3_storage_gb"]

        # Lambda functions (estimate 1M invocations/month, 1s duration)
        for func in resources.get("lambda", []):
            memory_mb = func.get("memory_size", 128)
            memory_gb = LAMBDA_MEMORY_TO_GB.get(memory_mb, 0.125)
            # 1M invocations * 1s * memory GB / 730 hours
            monthly_gb_seconds = 1_000_000 * 1 * memory_gb
            hourly_cost = monthly_gb_seconds * COST_PER_HOUR["lambda_gb_second"] / 730
            total_cost += hourly_cost

        # ECS services (assume 1vCPU-2GB per service)
        for service in resources.get("ecs", []):
            desired_count = service.get("desired_count", 1)
            vcpu, memory_gb = ECS_TASK_SIZES.get("1vCPU-2GB", (1.0, 2.0))
            service_cost = desired_count * COST_PER_HOUR["ecs_fargate_vcpu"] * vcpu
            service_cost += desired_count * COST_PER_HOUR["ecs_fargate_gb"] * memory_gb
            total_cost += service_cost

        # VPC costs (NAT gateways if present)
        for vpc in resources.get("vpc", []):
            # Check if VPC has NAT gateway (simplified check)
            if vpc.get("has_nat_gateway", False):
                total_cost += COST_PER_HOUR["nat_gateway"]

        return total_cost
