"""AWS infrastructure scanner for drift detection."""

import logging
from datetime import datetime
from typing import Any, Dict, List

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSScanner:
    """Scans AWS infrastructure and extracts configuration data."""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        config = Config(
            connect_timeout=5,
            read_timeout=60,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )
        self.session = boto3.Session(region_name=region)
        self.ec2 = self.session.client("ec2", config=config)
        self.rds = self.session.client("rds", config=config)
        self.s3 = self.session.client("s3", config=config)
        self.lambda_client = self.session.client("lambda", config=config)
        self.ecs = self.session.client("ecs", config=config)

    def scan_environment(self, environment: str) -> Dict[str, Any]:
        """Scan all resources for an environment."""
        logger.info(f"Scanning environment: {environment}")

        return {
            "environment": environment,
            "timestamp": datetime.utcnow().isoformat(),
            "region": self.region,
            "resources": {
                "vpc": self._scan_vpc(environment),
                "ec2": self._scan_ec2(environment),
                "rds": self._scan_rds(environment),
                "s3": self._scan_s3(environment),
                "lambda": self._scan_lambda(environment),
                "ecs": self._scan_ecs(environment),
            },
        }

    def _scan_vpc(self, environment: str) -> List[Dict[str, Any]]:
        """Scan VPC resources."""
        try:
            vpcs = self.ec2.describe_vpcs(
                Filters=[{"Name": "tag:Environment", "Values": [environment]}]
            )["Vpcs"]

            results = []
            for vpc in vpcs:
                vpc_id = vpc["VpcId"]
                subnets = self.ec2.describe_subnets(
                    Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                )["Subnets"]

                results.append(
                    {
                        "vpc_id": vpc_id,
                        "cidr_block": vpc["CidrBlock"],
                        "state": vpc["State"],
                        "tags": {
                            tag["Key"]: tag["Value"] for tag in vpc.get("Tags", [])
                        },
                        "subnets": [
                            {
                                "subnet_id": s["SubnetId"],
                                "cidr_block": s["CidrBlock"],
                                "availability_zone": s["AvailabilityZone"],
                            }
                            for s in subnets
                        ],
                    }
                )
            return results
        except ClientError as e:
            logger.error(f"VPC scan error: {e}")
            return []

    def _scan_ec2(self, environment: str) -> List[Dict[str, Any]]:
        """Scan EC2 instances."""
        try:
            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "tag:Environment", "Values": [environment]},
                    {"Name": "instance-state-name", "Values": ["running", "stopped"]},
                ]
            )

            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(
                        {
                            "instance_id": instance["InstanceId"],
                            "instance_type": instance["InstanceType"],
                            "state": instance["State"]["Name"],
                        }
                    )
            return instances
        except ClientError as e:
            logger.error(f"EC2 scan error: {e}")
            return []

    def _scan_rds(self, environment: str) -> List[Dict[str, Any]]:
        """Scan RDS instances."""
        try:
            instances = self.rds.describe_db_instances()["DBInstances"]
            results = []

            for instance in instances:
                tags = self.rds.list_tags_for_resource(
                    ResourceName=instance["DBInstanceArn"]
                )["TagList"]
                tag_dict = {tag["Key"]: tag["Value"] for tag in tags}

                if tag_dict.get("Environment") == environment:
                    results.append(
                        {
                            "db_instance_identifier": instance["DBInstanceIdentifier"],
                            "db_instance_class": instance["DBInstanceClass"],
                            "engine": instance["Engine"],
                        }
                    )
            return results
        except ClientError as e:
            logger.error(f"RDS scan error: {e}")
            return []

    def _scan_s3(self, environment: str) -> List[Dict[str, Any]]:
        """Scan S3 buckets."""
        try:
            buckets = self.s3.list_buckets()["Buckets"]
            results = []

            for bucket in buckets:
                try:
                    tags = self.s3.get_bucket_tagging(Bucket=bucket["Name"])["TagSet"]
                    tag_dict = {tag["Key"]: tag["Value"] for tag in tags}

                    if tag_dict.get("Environment") == environment:
                        results.append({"bucket_name": bucket["Name"]})
                except ClientError:
                    continue
            return results
        except ClientError as e:
            logger.error(f"S3 scan error: {e}")
            return []

    def _scan_lambda(self, environment: str) -> List[Dict[str, Any]]:
        """Scan Lambda functions."""
        try:
            functions = self.lambda_client.list_functions()["Functions"]
            results = []

            for function in functions:
                tags = self.lambda_client.list_tags(Resource=function["FunctionArn"])[
                    "Tags"
                ]
                if tags.get("Environment") == environment:
                    results.append(
                        {
                            "function_name": function["FunctionName"],
                            "runtime": function["Runtime"],
                            "memory_size": function["MemorySize"],
                        }
                    )
            return results
        except ClientError as e:
            logger.error(f"Lambda scan error: {e}")
            return []

    def _scan_ecs(self, environment: str) -> List[Dict[str, Any]]:
        """Scan ECS services."""
        try:
            clusters = self.ecs.list_clusters()["clusterArns"]
            results = []

            for cluster in clusters:
                services = self.ecs.list_services(cluster=cluster)["serviceArns"]
                if services:
                    described = self.ecs.describe_services(
                        cluster=cluster, services=services
                    )["services"]

                    for service in described:
                        tags = self.ecs.list_tags_for_resource(
                            resourceArn=service["serviceArn"]
                        )["tags"]
                        tag_dict = {tag["key"]: tag["value"] for tag in tags}

                        if tag_dict.get("Environment") == environment:
                            results.append(
                                {
                                    "service_name": service["serviceName"],
                                    "desired_count": service["desiredCount"],
                                }
                            )
            return results
        except ClientError as e:
            logger.error(f"ECS scan error: {e}")
            return []
