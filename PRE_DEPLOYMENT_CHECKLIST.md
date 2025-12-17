# Pre-Deployment Checklist

## ✅ Completed
- [x] Dockerfile created
- [x] Lambda handler implemented
- [x] Terraform configuration ready
- [x] CD pipeline configured
- [x] SNS topic exists
- [x] terraform.tfvars created
- [x] .gitignore updated

## 🔧 Required Before Deployment

### 1. GitHub Secrets (CRITICAL)
Add these to GitHub repo → Settings → Secrets and variables → Actions:
- [ ] `AWS_ACCESS_KEY_ID` - Your AWS access key
- [ ] `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

### 2. Deploy Infrastructure
```bash
cd terraform/lambda
terraform init
terraform plan
terraform apply
```

### 3. Verify Deployment
```bash
# Check ECR repository
aws ecr describe-repositories --repository-names drift-detection-lambda

# Check Lambda function
aws lambda get-function --function-name drift-detection

# Check EventBridge rule
aws events describe-rule --name drift-detection-daily
```

### 4. Test Lambda
```bash
# Manual invoke
aws lambda invoke --function-name drift-detection response.json
cat response.json

# Check logs
aws logs tail /aws/lambda/drift-detection --follow
```

### 5. Verify SNS Subscription
```bash
# Subscribe your email to SNS topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:900317037265:vprofile-pipeline-notifications \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription in email
```

## 🚀 Deployment Steps

1. **Merge branches**:
   ```bash
   git checkout develop
   git merge feature/add-sonarcloud
   git push origin develop

   git checkout main
   git merge develop
   git push origin main
   ```

2. **CD pipeline auto-triggers** on push to main:
   - Runs tests
   - Builds Docker image
   - Pushes to ECR
   - Updates Lambda function

3. **Monitor deployment**:
   - GitHub Actions → Check workflow status
   - AWS Console → Lambda → drift-detection

## 📊 Post-Deployment Verification

- [ ] Lambda function deployed successfully
- [ ] EventBridge rule active (daily 9 AM UTC)
- [ ] CloudWatch logs working
- [ ] SNS alerts configured
- [ ] Manual test successful
- [ ] First scheduled run completed

## 💰 Cost Monitoring

- [ ] Set up AWS Budget alert for $5/month
- [ ] Monitor Lambda invocations
- [ ] Check ECR storage usage

## 🎯 Success Criteria

- ✅ Lambda runs daily at 9 AM UTC
- ✅ Drift detection scans all 3 environments
- ✅ SNS alerts sent for HIGH/CRITICAL drift
- ✅ Reports saved to S3
- ✅ CloudWatch logs available
- ✅ Total cost < $1/month
