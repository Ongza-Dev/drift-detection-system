# Example Output

## Scenario: Production Environment Drift

### Setup
- **Baseline**: 1x t3.micro EC2, 1x db.t3.micro RDS
- **Current**: 1x t3.large EC2, 1x db.t3.micro RDS, 1x S3 bucket, 1x Lambda function
- **Changes**: EC2 upgraded, S3 added, Lambda added

### CLI Output

```bash
$ drift-detect --bucket drift-detection-prod-bucket detect prod

🚨 Drift detected in prod
  Drift detected: 2 added, 0 removed, 1 changed. Risk: CRITICAL
  Risk breakdown: 1 critical, 2 medium
  💰 Cost Impact: +$54.38/month (+276.4%)

  Recommendations:
    • ⚠️ CRITICAL: Immediate action required - review all changes
    • Verify added resources are authorized and properly tagged
    • Review configuration changes for security implications

  Report saved: reports/prod/20240115-143022.json
```

### Full Report JSON

```json
{
  "environment": "prod",
  "baseline_timestamp": "2024-01-15T10:00:00",
  "current_timestamp": "2024-01-15T14:30:22",
  "drift_detected": true,

  "summary": "Drift detected: 2 added, 0 removed, 1 changed. Risk: CRITICAL",

  "details": {
    "added": [
      "root['resources']['s3'][0]",
      "root['resources']['lambda'][0]"
    ],
    "removed": [],
    "changed": [
      "root['resources']['ec2'][0]['instance_type']"
    ]
  },

  "risk_assessment": {
    "overall_risk": "critical",
    "scored_changes": [
      {
        "change_path": "root['resources']['s3'][0]",
        "change_type": "added",
        "resource_type": "s3",
        "field_name": "unknown",
        "risk_level": "medium",
        "reason": "Storage changes can affect data access"
      },
      {
        "change_path": "root['resources']['lambda'][0]",
        "change_type": "added",
        "resource_type": "lambda",
        "field_name": "unknown",
        "risk_level": "medium",
        "reason": "Function changes may break integrations"
      },
      {
        "change_path": "root['resources']['ec2'][0]['instance_type']",
        "change_type": "changed",
        "resource_type": "ec2",
        "field_name": "instance_type",
        "risk_level": "critical",
        "reason": "Compute changes affect performance and cost - Critical field 'instance_type' modified"
      }
    ],
    "risk_distribution": {
      "critical": 1,
      "high": 0,
      "medium": 2,
      "low": 0,
      "info": 0
    }
  },

  "cost_impact": {
    "baseline_monthly_cost": 19.67,
    "current_monthly_cost": 74.05,
    "monthly_impact": 54.38,
    "impact_percentage": 276.4
  },

  "recommendations": [
    "⚠️ CRITICAL: Immediate action required - review all changes",
    "Verify added resources are authorized and properly tagged",
    "Review configuration changes for security implications",
    "Update baseline if changes are intentional"
  ]
}
```

### Cost Breakdown

#### Baseline Cost: $19.67/month
- EC2 t3.micro (running): $0.0104/hr × 730 = $7.59
- RDS db.t3.micro: $0.017/hr × 730 = $12.41
- **Total**: $19.67/month

#### Current Cost: $74.05/month
- EC2 t3.large (running): $0.0832/hr × 730 = $60.74
- RDS db.t3.micro: $0.017/hr × 730 = $12.41
- S3 (10GB): $0.023/month = $0.23
- Lambda (1M invocations, 128MB, 1s): ~$0.67
- **Total**: $74.05/month

#### Impact: +$54.38/month (+276.4%)

### Risk Analysis

#### Critical Risk (1 change)
- **EC2 instance_type changed**: t3.micro → t3.large
  - Base risk: HIGH (compute resource)
  - Field risk: CRITICAL (instance_type is critical field)
  - Final risk: CRITICAL (elevated)
  - Impact: Performance change, 8x cost increase

#### Medium Risk (2 changes)
- **S3 bucket added**
  - Base risk: MEDIUM (storage resource)
  - Change type: MEDIUM (added resource)
  - Final risk: MEDIUM
  - Impact: New data storage, minimal cost

- **Lambda function added**
  - Base risk: MEDIUM (serverless resource)
  - Change type: MEDIUM (added resource)
  - Final risk: MEDIUM
  - Impact: New compute capability, variable cost

### Action Items

1. **Immediate** (CRITICAL risk)
   - Verify EC2 instance type change was authorized
   - Check if t3.large is required or if t3.micro was sufficient
   - Review performance metrics to justify upgrade
   - Consider cost optimization (Reserved Instances, Savings Plans)

2. **Within 24 hours** (MEDIUM risk)
   - Verify S3 bucket has proper access controls
   - Confirm Lambda function is properly tagged
   - Review Lambda execution role permissions
   - Ensure new resources follow security policies

3. **Follow-up**
   - Update baseline if changes are approved
   - Document reason for infrastructure changes
   - Set up alerts for future CRITICAL drift
   - Review cost optimization opportunities

## Scenario: No Drift Detected

```bash
$ drift-detect --bucket drift-detection-dev-bucket detect dev

✓ No drift detected in dev

  Report saved: reports/dev/20240115-143025.json
```

## Scenario: Cost Decrease

```bash
$ drift-detect --bucket drift-detection-staging-bucket detect staging

⚠ Drift detected in staging
  Drift detected: 0 added, 1 removed, 1 changed. Risk: CRITICAL
  Risk breakdown: 1 critical, 1 high
  💰 Cost Impact: -$112.41/month (-90.3%)

  Recommendations:
    • ⚠️ CRITICAL: Immediate action required - review all changes
    • Investigate removed resources - potential data loss risk
    • Review configuration changes for security implications

  Report saved: reports/staging/20240115-143030.json
```

**Analysis**: RDS instance removed (CRITICAL risk) and EC2 downgraded. Cost savings significant but removal of database is high-risk change requiring immediate investigation.
