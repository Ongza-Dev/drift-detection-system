# Multi-Environment Drift Detection System

[![CI](https://github.com/Ongza-Dev/drift-detection-system/workflows/CI/badge.svg)](https://github.com/Ongza-Dev/drift-detection-system/actions)
[![Deploy](https://github.com/Ongza-Dev/drift-detection-system/workflows/Deploy%20to%20Production/badge.svg)](https://github.com/Ongza-Dev/drift-detection-system/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Ongza-Dev_drift-detection-system&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Ongza-Dev_drift-detection-system)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Ongza-Dev_drift-detection-system&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Ongza-Dev_drift-detection-system)

## 🚀 Production Status: LIVE

**Deployed on AWS Lambda** | **Running Daily at 9 AM SAST** | **Monitoring 3 Environments**

## Project Overview
Production-grade serverless system that automatically detects infrastructure drift across dev/staging/prod environments, scores the risk of each drift, and quantifies the monthly cost impact of configuration mismatches.

## ✅ Deployment Status
✅ **AWS Lambda deployed** - Serverless execution
✅ **EventBridge scheduled** - Daily automated scans (9 AM SAST)
✅ **ECR container registry** - Docker image deployment
✅ **SNS alerting** - HIGH/CRITICAL drift notifications
✅ **Dead Letter Queue** - Failed invocation handling
✅ **CloudWatch monitoring** - 7-day log retention
✅ **CI/CD pipeline** - Automated testing and deployment
✅ **SonarCloud integration** - Code quality gate passing
✅ **85% test coverage** - 43 tests passing
✅ **IAM least privilege** - Scoped permissions
✅ **Cost optimized** - ~$0.35/month total

## 🏗️ Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud (us-east-1)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌─────────────────────────────┐    │
│  │ EventBridge  │──────▶│   Lambda Function          │    │
│  │ (Daily 9 AM) │      │   - Docker Container        │    │
│  └──────────────┘      │   - 512MB Memory            │    │
│                        │   - 5min Timeout            │    │
│                        └─────────────────────────────┘    │
│                                    │                       │
│                    ┌───────────────┼───────────────┐       │
│                    ▼               ▼               ▼       │
│            ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│            │   ECR    │    │    S3    │    │   SNS    │   │
│            │  Image   │    │ Baselines│    │  Alerts  │   │
│            │ Registry │    │ & Reports│    │          │   │
│            └──────────┘    └──────────┘    └──────────┘   │
│                                                             │
│  Scans: VPC, EC2, RDS, S3, Lambda, ECS across 3 envs      │
└─────────────────────────────────────────────────────────────┘
```

## 💰 Production Cost Breakdown

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 30 invocations/month, 5min each, 512MB | $0.10 |
| ECR | 500MB Docker image storage | $0.10 |
| S3 | Drift detection data storage | $0.10 |
| CloudWatch Logs | 7-day retention | $0.05 |
| SQS DLQ | Dead letter queue (minimal usage) | $0.00 |
| EventBridge | Scheduled rules | $0.00 (free tier) |
| **Total** | | **~$0.35/month** |

## Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0 installed
- Python >= 3.8 installed
- Git installed
- Docker Desktop (for local builds)

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

## 🚀 Production Deployment

### Deploy to AWS Lambda

1. **Add GitHub Secrets**
   ```
   Repository → Settings → Secrets → Actions
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   ```

2. **Deploy Infrastructure**
   ```bash
   cd terraform/lambda
   terraform init
   terraform apply
   ```

3. **Trigger Deployment**
   - Push to `main` branch (automatic)
   - Or manually: GitHub → Actions → Deploy to Production → Run workflow

4. **Create Baselines**
   ```bash
   drift-detect --bucket <your-bucket> baseline dev
   drift-detect --bucket <your-bucket> baseline staging
   drift-detect --bucket <your-bucket> baseline prod
   ```

5. **Subscribe to Alerts**
   ```bash
   aws sns subscribe \
     --topic-arn <your-sns-topic-arn> \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```

### Verify Deployment

```bash
# Test Lambda function
aws lambda invoke --function-name drift-detection response.json
cat response.json

# Check logs
aws logs tail /aws/lambda/drift-detection --follow

# Verify EventBridge rule
aws events describe-rule --name drift-detection-daily
```

## 🔄 CI/CD Pipeline

### Continuous Integration (CI)
- **Trigger**: Pull requests and pushes to `develop`/`main`
- **Steps**: Linting (black, isort, flake8) → Testing → Coverage → SonarCloud
- **Quality Gates**: 80% coverage minimum, all tests passing

### Continuous Deployment (CD)
- **Trigger**: Push to `main` branch
- **Steps**: Build Docker image → Push to ECR → Update Lambda function
- **Automation**: Zero-downtime deployments

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

### Automated Alerting
- SNS notifications for HIGH/CRITICAL drift
- Email alerts with risk assessment
- Cost impact analysis in alerts
- Actionable recommendations

## 📊 Monitoring & Observability

### CloudWatch Metrics
- Lambda invocations (daily)
- Error rates and duration
- Memory utilization

### Logs
- Structured logging with timestamps
- Per-environment scan results
- Error tracking and debugging

### Alerts
- SNS notifications for HIGH/CRITICAL drift
- Email alerts with detailed reports
- Dead letter queue for failed invocations

## 🛡️ Security & Best Practices

✅ **IAM Least Privilege** - Scoped permissions (no wildcards)
✅ **Secrets Management** - GitHub Secrets for AWS credentials
✅ **Error Handling** - Comprehensive try-catch blocks
✅ **Retry Logic** - Adaptive retry with exponential backoff
✅ **Timeout Configuration** - 5s connect, 60s read timeouts
✅ **Dead Letter Queue** - Failed invocation tracking
✅ **CloudWatch Monitoring** - Centralized logging
✅ **Container Scanning** - ECR image vulnerability scanning

## 🎯 Key Achievements

- ✅ **Production-grade serverless architecture** on AWS Lambda
- ✅ **Fully automated CI/CD pipeline** with GitHub Actions
- ✅ **85% test coverage** with comprehensive test suite
- ✅ **SonarCloud quality gate passing** - zero code smells
- ✅ **Cost-optimized** - runs for ~$0.35/month
- ✅ **Security hardened** - IAM least privilege, no wildcards
- ✅ **Monitoring & alerting** - CloudWatch + SNS integration
- ✅ **Zero-downtime deployments** - containerized Lambda updates

## 📚 Documentation
- [Architecture Details](docs/architecture.md)
- [Lambda Deployment Guide](docs/LAMBDA_DEPLOYMENT.md)
- [SNS Setup](docs/SNS_SETUP.md)
- [Contributing Guidelines](CONTRIBUTING.md)
