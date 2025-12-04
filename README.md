# Multi-Environment Drift Detection System

## Project Overview
Production-ready system that detects infrastructure drift across dev/staging/prod environments, scores the risk of each drift, and quantifies the monthly cost impact of configuration mismatches.

## Setup Status
✅ Project structure created
✅ Terraform backend with S3 + DynamoDB deployed
✅ VPC infrastructure deployed (dev/staging/prod)
✅ S3 storage module for drift detection data
✅ Python application with scanner, comparator, reporter
✅ Risk scoring system (CRITICAL → INFO)
✅ Complete cost analysis (all 6 resource types)
✅ CLI interface with structured logging
✅ Comprehensive test suite (31 tests, all passing, 87% coverage)
✅ Development environment with pre-commit hooks

## Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0 installed
- Python >= 3.8 installed
- Git installed

## Quick Start

### 1. Install Application
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -e .
```

### 2. Set Environment Variables
```bash
export AWS_REGION=us-east-1
export AWS_PROFILE=default
```

### 3. Use CLI
```bash
# Create baseline for dev environment
drift-detect --bucket drift-detection-dev-bucket baseline dev

# Scan current state
drift-detect --bucket drift-detection-dev-bucket scan dev

# Detect drift with risk scoring and cost analysis
drift-detect --bucket drift-detection-dev-bucket detect dev

# Example output:
# 🚨 Drift detected in dev
#   Drift detected: 1 added, 0 removed, 1 changed. Risk: CRITICAL
#   Risk breakdown: 1 critical, 1 medium
#   💰 Cost Impact: +$54.38/month (+276.4%)
#
#   Recommendations:
#     • ⚠️ CRITICAL: Immediate action required - review all changes
#     • Verify added resources are authorized and properly tagged
#     • Review configuration changes for security implications

# Detect across all environments
drift-detect --bucket drift-detection-dev-bucket detect-all
```

### 4. Run Tests
```bash
cmd /c "venv\Scripts\pytest.exe tests -v --cov"
```

## Architecture
See [docs/architecture.md](docs/architecture.md) for detailed system design.

## Features

### Drift Detection
- Scans 6 AWS resource types (VPC, EC2, RDS, S3, Lambda, ECS)
- Deep configuration comparison using DeepDiff
- Multi-environment support (dev/staging/prod)
- S3-based storage with versioning

### Risk Scoring
- 5-level risk classification (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Resource-based risk weighting
- Critical field detection (instance_type, db_instance_class, etc.)
- Risk distribution reporting

### Cost Analysis
- Complete coverage of all scanned resource types
- Monthly cost impact calculation
- Percentage change reporting
- Handles cost increases and decreases

### CLI Output
- Risk emoji indicators (🚨 critical, ⚠️ high, ⚠ medium, ℹ️ low)
- Risk breakdown by severity
- Cost impact with percentage change
- Prioritized recommendations

## Current Infrastructure Cost
- Dev environment: ~$0.10/month (S3 storage only)
- Staging/Prod: VPC only (no additional cost)
- Total: <$1/month
