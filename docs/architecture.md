# Drift Detection System Architecture

## Overview
Production-grade serverless system that automatically detects infrastructure drift across dev/staging/prod environments, scores risk, and quantifies cost impact.

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

## Components

### Lambda Function
- **Runtime**: Python 3.12 (Docker container)
- **Memory**: 512MB
- **Timeout**: 5 minutes
- **Concurrency**: Unreserved (cost-optimized)
- **Trigger**: EventBridge scheduled rule (daily 9 AM SAST / 7 AM UTC)
- **Error Handling**: Dead Letter Queue (SQS)

### ECR Repository
- **Name**: drift-detection-lambda
- **Image Scanning**: Enabled on push
- **Tag Mutability**: Mutable
- **Storage**: ~500MB

### S3 Storage
- **Bucket**: drift-detection-drift-detection-dev-026bfe5b
- **Structure**:
  - `baselines/{environment}/baseline.json` - Reference configurations
  - `scans/{environment}/{timestamp}.json` - Scan results
  - `reports/{environment}/{timestamp}.json` - Drift reports with risk/cost analysis
- **Versioning**: Enabled

### EventBridge Rule
- **Name**: drift-detection-daily
- **Schedule**: cron(0 7 * * ? *) - Daily at 9 AM SAST
- **Target**: Lambda function

### SNS Topic
- **ARN**: arn:aws:sns:us-east-1:900317037265:vprofile-pipeline-notifications
- **Purpose**: HIGH/CRITICAL drift alerts
- **Protocol**: Email

### SQS Dead Letter Queue
- **Name**: drift-detection-dlq
- **Retention**: 14 days
- **Purpose**: Failed Lambda invocations

### CloudWatch Logs
- **Log Group**: /aws/lambda/drift-detection
- **Retention**: 7 days
- **Purpose**: Execution logs, errors, drift detection results

## Monitored Environments

### Dev Environment (10.0.0.0/16)
- VPC with public/private subnets
- EC2 instances (if any)
- RDS databases (if any)
- S3 buckets tagged with Environment=dev
- Lambda functions tagged with Environment=dev
- ECS services tagged with Environment=dev

### Staging Environment (10.1.0.0/16)
- VPC with public/private subnets
- EC2 instances (if any)
- RDS databases (if any)
- S3 buckets tagged with Environment=staging
- Lambda functions tagged with Environment=staging
- ECS services tagged with Environment=staging

### Production Environment (10.2.0.0/16)
- VPC with public/private subnets
- EC2 instances (if any)
- RDS databases (if any)
- S3 buckets tagged with Environment=prod
- Lambda functions tagged with Environment=prod
- ECS services tagged with Environment=prod

## Drift Detection Flow

1. **EventBridge Trigger** - Daily at 9 AM SAST
2. **Lambda Invocation** - Starts drift detection process
3. **Scan Phase** - For each environment:
   - Scan VPC configurations
   - Scan EC2 instances
   - Scan RDS databases
   - Scan S3 buckets
   - Scan Lambda functions
   - Scan ECS services
4. **Comparison Phase** - Compare current state vs baseline
5. **Risk Scoring** - Classify drift by severity (CRITICAL → INFO)
6. **Cost Analysis** - Calculate monthly cost impact
7. **Report Generation** - Create detailed drift report
8. **Storage** - Save report to S3
9. **Alerting** - Send SNS notification if HIGH/CRITICAL drift detected

## Security

### IAM Permissions (Least Privilege)
- **EC2**: DescribeVpcs, DescribeSubnets, DescribeInstances
- **RDS**: DescribeDBInstances, ListTagsForResource
- **S3**: GetObject, PutObject, ListBucket, GetBucketTagging (scoped to drift bucket + read-only for scanning)
- **Lambda**: ListFunctions, ListTags
- **ECS**: ListClusters, ListServices, DescribeServices, ListTagsForResource
- **SNS**: Publish (scoped to specific topic)
- **SQS**: SendMessage (scoped to DLQ)
- **CloudWatch Logs**: CreateLogGroup, CreateLogStream, PutLogEvents (scoped to Lambda log group)

### Error Handling
- Comprehensive try-catch blocks in Lambda handler
- Per-environment error isolation
- Proper error responses (500 status codes)
- Dead Letter Queue for failed invocations

### Retry Logic
- Boto3 adaptive retry mode
- 3 max attempts
- 5s connect timeout
- 60s read timeout

## CI/CD Pipeline

### Continuous Integration
- **Trigger**: Push to develop/main, pull requests
- **Steps**:
  1. Linting (black, isort, flake8)
  2. Testing (pytest with 85% coverage)
  3. SonarCloud quality gate
- **Quality Gates**: 80% coverage minimum, all tests passing

### Continuous Deployment
- **Trigger**: Push to main branch
- **Steps**:
  1. Run tests
  2. Build Docker image
  3. Push to ECR
  4. Update Lambda function
- **Automation**: Zero-downtime deployments

## Cost Breakdown

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 30 invocations/month, 5min each, 512MB | $0.10 |
| ECR | 500MB Docker image storage | $0.10 |
| S3 | Drift detection data storage | $0.10 |
| CloudWatch Logs | 7-day retention | $0.05 |
| SQS DLQ | Dead letter queue (minimal usage) | $0.00 |
| EventBridge | Scheduled rules | $0.00 (free tier) |
| **Total** | | **~$0.35/month** |

## Monitoring & Observability

### CloudWatch Metrics
- Lambda invocations (daily)
- Error rates and duration
- Memory utilization
- DLQ message count

### Logs
- Structured logging with timestamps
- Per-environment scan results
- Error tracking and debugging
- Drift detection summaries

### Alerts
- SNS notifications for HIGH/CRITICAL drift
- Email alerts with risk assessment
- Cost impact analysis in alerts
- Actionable recommendations

## Scalability

- **Serverless**: Auto-scales with demand
- **Stateless**: No persistent connections
- **Concurrent Executions**: Unreserved (can scale to account limits)
- **Storage**: S3 scales automatically

## Disaster Recovery

- **Lambda**: Managed by AWS, multi-AZ by default
- **S3**: 99.999999999% durability, versioning enabled
- **ECR**: Replicated across AZs
- **DLQ**: 14-day retention for failed invocations
- **Logs**: 7-day retention in CloudWatch

## Future Enhancements

- Add pagination for large resource sets
- Improve cost estimation accuracy with CloudWatch metrics
- Add Slack notifications
- Add drift remediation suggestions
- Add Terraform state drift detection
- Add compliance checks (tagging policies, encryption)
- Add CloudWatch dashboard for metrics
- Add X-Ray tracing for Lambda
