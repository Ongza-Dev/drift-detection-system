# Drift Detection System Architecture

## Overview
Multi-environment drift detection system with cost impact analysis for AWS infrastructure.

## Network Architecture

### VPC Design
- **Dev Environment**: 10.0.0.0/16
  - Public Subnets: 10.0.1.0/24, 10.0.2.0/24
  - Private Subnets: 10.0.10.0/24, 10.0.20.0/24

- **Staging Environment**: 10.1.0.0/16
  - Public Subnets: 10.1.1.0/24, 10.1.2.0/24
  - Private Subnets: 10.1.10.0/24, 10.1.20.0/24

- **Production Environment**: 10.2.0.0/16
  - Public Subnets: 10.2.1.0/24, 10.2.2.0/24
  - Private Subnets: 10.2.10.0/24, 10.2.20.0/24

### Components per Environment
- ECS Cluster (Fargate)
- Application Load Balancer
- Security Groups
- NAT Gateways for private subnet internet access

### Shared Resources
- RDS PostgreSQL (Multi-AZ for prod)
- ElastiCache Redis
- Lambda functions for drift detection
- S3 buckets for state and reports
- CloudWatch logs and monitoring

## Security
- All resources in private subnets except ALB
- IAM roles with least privilege
- Secrets in AWS Parameter Store
- VPC Flow Logs enabled
- Security groups with minimal required access

## Cost Optimization
- Fargate Spot pricing where possible
- RDS db.t3.micro instances
- ElastiCache t3.micro nodes
- Lifecycle policies on S3 buckets
- CloudWatch log retention policies
