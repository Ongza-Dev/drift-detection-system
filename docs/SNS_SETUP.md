# SNS Alerting Setup

## Quick Setup (5 minutes)

### 1. Get Your SNS Topic ARN

From AWS Console or CLI:
```bash
aws sns list-topics
```

Look for your topic ARN (format: `arn:aws:sns:us-east-1:123456789012:drift-alerts`)

### 2. Use with Drift Detection

```bash
# With SNS alerts (sends email for HIGH/CRITICAL drift)
drift-detect \
  --bucket drift-detection-dev-bucket \
  --sns-topic arn:aws:sns:us-east-1:123456789012:drift-alerts \
  detect dev

# Without SNS alerts (original behavior)
drift-detect --bucket drift-detection-dev-bucket detect dev
```

## How It Works

**Alert Threshold**: Only sends alerts for HIGH or CRITICAL risk drift
- ✅ CRITICAL risk → Email sent
- ✅ HIGH risk → Email sent
- ❌ MEDIUM risk → No email
- ❌ LOW risk → No email
- ❌ INFO (no drift) → No email

**Email Format**:
```
Subject: 🚨 CRITICAL Drift Detected: prod

Environment: prod
Risk Level: CRITICAL

Summary: Drift detected: 1 added, 0 removed, 1 changed. Risk: CRITICAL

Risk Breakdown:
  - Critical: 1
  - Medium: 1

Cost Impact: +$54.38/month (+276.4%)

Recommendations:
  • ⚠️ CRITICAL: Immediate action required - review all changes
  • Verify added resources are authorized and properly tagged
  • Review configuration changes for security implications
```

## Environment Variable (Optional)

Set once instead of passing flag every time:

```bash
export DRIFT_SNS_TOPIC=arn:aws:sns:us-east-1:123456789012:drift-alerts

# Then use without --sns-topic flag
drift-detect --bucket my-bucket detect prod
```

Update CLI to read from environment:
```python
@click.option("--sns-topic",
              default=lambda: os.environ.get('DRIFT_SNS_TOPIC'),
              help="SNS topic ARN for alerts")
```

## Scheduled Scanning with Alerts

Run daily via cron:

```bash
# Add to crontab
0 9 * * * drift-detect --bucket my-bucket --sns-topic arn:aws:sns:... detect-all
```

Or use AWS EventBridge + Lambda for fully managed solution.

## Cost

**SNS Pricing**:
- First 1,000 email notifications/month: FREE
- After that: $2 per 100,000 notifications

**Your cost**: $0 (unless you detect >1,000 high-risk drifts/month)

## Testing

Test the alert:

```bash
# 1. Make a change to trigger drift (e.g., change VPC tag)
aws ec2 create-tags --resources vpc-xxx --tags Key=Test,Value=Alert

# 2. Run detection with SNS
drift-detect --bucket my-bucket --sns-topic arn:aws:sns:... detect dev

# 3. Check your email
```

## Troubleshooting

**No email received?**
1. Check SNS subscription is confirmed (check email for confirmation link)
2. Verify drift risk is HIGH or CRITICAL (MEDIUM won't trigger alert)
3. Check AWS CloudWatch Logs for SNS publish errors
4. Verify IAM permissions for SNS:Publish

**IAM Policy Needed**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sns:Publish",
    "Resource": "arn:aws:sns:us-east-1:123456789012:drift-alerts"
  }]
}
```
