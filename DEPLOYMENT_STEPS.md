# Lambda Deployment - Quick Start

## What You Have

✅ Lambda handler (`lambda/handler.py`)
✅ Dockerfile for containerized deployment
✅ Terraform infrastructure code
✅ GitHub Actions CI/CD pipeline
✅ Makefile for DevOps commands

## Deploy to AWS (15 minutes)

### 1. Configure Terraform Variables

```bash
cd terraform/lambda
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# drift_bucket   = "drift-detection-drift-detection-dev-026bfe5b"
# sns_topic_arn  = "arn:aws:sns:us-east-1:900317037265:vprofile-pipeline-notifications"
```

### 2. Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

Creates: ECR repo, Lambda function, IAM role, EventBridge schedule

### 3. Build and Push Container

```bash
# Get ECR URL from Terraform output
ECR_URL=$(terraform output -raw ecr_repository_url)

# Build image
cd ../..
docker build -t $ECR_URL:latest -f lambda/Dockerfile .

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL

# Push image
docker push $ECR_URL:latest
```

### 4. Test Lambda

```bash
# Invoke manually
aws lambda invoke --function-name drift-detection --payload '{}' response.json

# View logs
aws logs tail /aws/lambda/drift-detection --follow
```

## Automated Deployments (GitHub Actions)

### Setup

1. Push code to GitHub
2. Add secrets to repository:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

### Deploy

```bash
git add .
git commit -m "Deploy Lambda"
git push origin main
```

GitHub Actions automatically:
- Runs tests
- Builds container
- Pushes to ECR
- Updates Lambda

## Using Makefile

```bash
make test           # Run tests
make build          # Build Docker image
make deploy-infra   # Deploy with Terraform
make deploy-lambda  # Build and deploy Lambda
```

## What Happens

**Daily at 9 AM UTC:**
1. EventBridge triggers Lambda
2. Lambda scans dev/staging/prod
3. Detects drift, scores risk
4. Sends SNS alerts for HIGH/CRITICAL
5. Saves reports to S3
6. Logs to CloudWatch

## Cost

- Lambda: $0.20/month
- ECR: $0.10/month
- CloudWatch: $0.50/month
- **Total: ~$0.80/month**

## Next Steps

1. Deploy infrastructure: `make deploy-infra`
2. Build and push: `make deploy-lambda`
3. Test: `aws lambda invoke --function-name drift-detection --payload '{}' response.json`
4. Setup GitHub Actions for automated deployments
5. Monitor: `aws logs tail /aws/lambda/drift-detection --follow`
