# Lambda Deployment Guide

## Architecture

```
GitHub → GitHub Actions → ECR → Lambda → EventBridge (Daily 9 AM)
```

## Prerequisites

1. AWS CLI configured
2. Terraform installed
3. Docker installed
4. GitHub repository (for CI/CD)

## Manual Deployment (First Time)

### Step 1: Deploy Infrastructure

```bash
cd terraform/lambda

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
# terraform.tfvars:
# drift_bucket   = "your-bucket-name"
# sns_topic_arn  = "your-sns-topic-arn"

# Deploy
terraform init
terraform plan
terraform apply
```

This creates:
- ECR repository
- Lambda function
- IAM role with permissions
- EventBridge schedule (daily 9 AM)
- CloudWatch log group

### Step 2: Build and Push Container

```bash
# Get ECR URL
ECR_URL=$(cd terraform/lambda && terraform output -raw ecr_repository_url)

# Build Docker image
docker build -t $ECR_URL:latest -f lambda/Dockerfile .

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Push image
docker push $ECR_URL:latest
```

### Step 3: Update Lambda

```bash
aws lambda update-function-code \
  --function-name drift-detection \
  --image-uri $ECR_URL:latest
```

### Step 4: Test Lambda

```bash
# Invoke manually
aws lambda invoke \
  --function-name drift-detection \
  --payload '{}' \
  response.json

# Check logs
aws logs tail /aws/lambda/drift-detection --follow
```

## Automated Deployment (CI/CD)

### Setup GitHub Secrets

Add to GitHub repository secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Trigger Deployment

```bash
git add .
git commit -m "Deploy to Lambda"
git push origin main
```

GitHub Actions will:
1. Run tests
2. Build Docker image
3. Push to ECR
4. Update Lambda function

## Using Makefile

```bash
# Run tests
make test

# Build locally
make build

# Deploy infrastructure
make deploy-infra

# Deploy Lambda
make deploy-lambda
```

## Monitoring

### View Logs

```bash
aws logs tail /aws/lambda/drift-detection --follow
```

### Check Schedule

```bash
aws events list-rules --name-prefix drift-detection
```

### Manual Trigger

```bash
aws lambda invoke \
  --function-name drift-detection \
  --payload '{}' \
  response.json
```

## Cost

- Lambda: ~$0.20/month (300 seconds × 30 days × $0.0000166667/GB-second)
- ECR: ~$0.10/month (storage)
- CloudWatch Logs: ~$0.50/month (7 days retention)
- **Total: ~$0.80/month**

## Troubleshooting

### Lambda timeout

Increase timeout in `terraform/lambda/main.tf`:
```hcl
timeout = 600  # 10 minutes
```

### Permission errors

Check IAM role has required permissions in `terraform/lambda/main.tf`

### Container build fails

Test locally:
```bash
docker build -t drift-detection:test -f lambda/Dockerfile .
docker run --rm drift-detection:test
```

## Rollback

```bash
# List image versions
aws ecr list-images --repository-name drift-detection-lambda

# Update to specific version
aws lambda update-function-code \
  --function-name drift-detection \
  --image-uri $ECR_URL:PREVIOUS_SHA
```

## Cleanup

```bash
cd terraform/lambda
terraform destroy
```
