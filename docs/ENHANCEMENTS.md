# System Enhancements

## Overview
Added risk scoring and comprehensive cost analysis to complete the drift detection system's core value proposition.

## New Features

### 1. Risk Scoring (risk_scorer.py)

**Purpose**: Prioritize drift by severity to enable actionable responses.

**Risk Levels**:
- `CRITICAL`: Immediate action required (removed resources, critical field changes)
- `HIGH`: Review within 24 hours (VPC, EC2, ECS changes)
- `MEDIUM`: Review soon (S3, Lambda changes, added resources)
- `LOW`: Informational
- `INFO`: No drift detected

**Risk Calculation**:
- Base risk by resource type (RDS=CRITICAL, VPC/EC2/ECS=HIGH, S3/Lambda=MEDIUM)
- Elevated risk for critical fields (instance_type, db_instance_class, cidr_block, etc.)
- Change type weighting (removed=CRITICAL, added/changed=MEDIUM)
- Overall risk = highest individual risk

**Example Output**:
```json
{
  "overall_risk": "critical",
  "scored_changes": [
    {
      "change_path": "root['resources']['rds'][0]",
      "change_type": "removed",
      "resource_type": "rds",
      "risk_level": "critical",
      "reason": "Database changes can cause downtime or data loss - Resource removed"
    }
  ],
  "risk_distribution": {
    "critical": 1,
    "high": 0,
    "medium": 2,
    "low": 0,
    "info": 0
  }
}
```

### 2. Enhanced Cost Analysis (cost_analyzer.py)

**Purpose**: Quantify financial impact of ALL infrastructure drift, not just compute.

**New Coverage**:
- **S3**: $0.023/GB/month (assumes 10GB per bucket)
- **Lambda**: $0.0000166667 per GB-second (assumes 1M invocations/month, 1s duration)
- **ECS Fargate**: $0.04048/vCPU/hour + $0.004445/GB/hour
- **VPC NAT Gateway**: $0.045/hour (if present)
- **EC2**: Now only counts running instances (stopped instances = $0)

**Cost Impact Output**:
```json
{
  "baseline_monthly_cost": 15.23,
  "current_monthly_cost": 75.89,
  "monthly_impact": 60.66,
  "impact_percentage": 398.29
}
```

### 3. Enhanced Reporting (reporter.py)

**Changes**:
- Integrated risk assessment into all reports
- Risk-based recommendations (critical/high priority alerts)
- Summary includes risk level
- Recommendations prioritized by severity

**Example Report**:
```json
{
  "environment": "prod",
  "drift_detected": true,
  "summary": "Drift detected: 1 added, 1 removed, 2 changed. Risk: CRITICAL",
  "risk_assessment": { ... },
  "cost_impact": { ... },
  "recommendations": [
    "⚠️ CRITICAL: Immediate action required - review all changes",
    "Investigate removed resources - potential data loss risk",
    "Review configuration changes for security implications"
  ]
}
```

### 4. Enhanced CLI (cli.py)

**Display Improvements**:
- Risk emoji indicators (🚨 critical, ⚠️ high, ⚠ medium, ℹ️ low)
- Risk distribution breakdown
- Improved cost formatting with percentage change
- Top 3 recommendations displayed
- Better visual hierarchy

**Example Output**:
```
🚨 Drift detected in prod
  Drift detected: 1 added, 1 removed, 2 changed. Risk: CRITICAL
  Risk breakdown: 1 critical, 2 medium
  💰 Cost Impact: +$60.66/month (+398.3%)

  Recommendations:
    • ⚠️ CRITICAL: Immediate action required - review all changes
    • Investigate removed resources - potential data loss risk
    • Review configuration changes for security implications

  Report saved: reports/prod/20240115-143022.json
```

## Testing

**New Test Files**:
- `test_risk_scorer.py`: 8 tests covering all risk scenarios
- `test_cost_analyzer_enhanced.py`: 7 tests for all resource types
- Updated `test_reporter.py`: Validates risk assessment integration

**Test Coverage**:
- Risk scoring: All severity levels, resource types, change types
- Cost analysis: All 6 resource types, cost increases/decreases
- Integration: Risk + cost in reports

## Impact

### Before
- ✅ Detected drift
- ❌ No prioritization (all drift treated equally)
- ⚠️ Partial cost analysis (EC2/RDS only)

### After
- ✅ Detects drift
- ✅ Scores risk (CRITICAL → INFO)
- ✅ Complete cost analysis (all 6 resource types)
- ✅ Actionable recommendations
- ✅ Production-ready prioritization

## Usage

No API changes required. Existing commands work with enhanced output:

```bash
# Same command, richer output
drift-detect --bucket my-bucket detect prod
```

## Architecture

```
Scanner → Comparator → [Risk Scorer] → Reporter → CLI
                    ↘ [Cost Analyzer] ↗
```

**New Dependencies**: None (uses existing libraries)

**Breaking Changes**: None (backward compatible)

## Next Steps

Recommended future enhancements:
1. Alerting (SNS/Slack) for CRITICAL/HIGH risks
2. Scheduled scanning (EventBridge + Lambda)
3. Historical trend analysis
4. Drift auto-remediation for approved changes
5. Custom risk rules per environment
