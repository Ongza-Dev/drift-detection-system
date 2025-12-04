# Cron Job Setup for Automatic Drift Detection

## Step 1: Configure the Script

Edit `scripts/run-drift-detection.sh` and replace `YOUR_SNS_TOPIC_ARN`:

```bash
SNS_TOPIC="arn:aws:sns:us-east-1:123456789012:drift-alerts"
```

## Step 2: Make Script Executable

```bash
chmod +x scripts/run-drift-detection.sh
```

## Step 3: Test the Script

```bash
./scripts/run-drift-detection.sh
```

Check the log:
```bash
tail -f /tmp/drift-detection.log
```

## Step 4: Add to Crontab

Open crontab editor:
```bash
crontab -e
```

Add one of these schedules:

### Every 6 hours
```bash
0 */6 * * * /c/Project/drift-detection-system/scripts/run-drift-detection.sh
```

### Daily at 9 AM
```bash
0 9 * * * /c/Project/drift-detection-system/scripts/run-drift-detection.sh
```

### Twice daily (9 AM and 9 PM)
```bash
0 9,21 * * * /c/Project/drift-detection-system/scripts/run-drift-detection.sh
```

### Every hour (aggressive)
```bash
0 * * * * /c/Project/drift-detection-system/scripts/run-drift-detection.sh
```

## Step 5: Verify Cron Job

List your cron jobs:
```bash
crontab -l
```

## What Happens Now

1. **Cron runs script** at scheduled time
2. **Script activates venv** and runs drift detection
3. **Detects drift** across all environments (dev/staging/prod)
4. **Sends email** if HIGH or CRITICAL risk detected
5. **Logs output** to `/tmp/drift-detection.log`

## Monitoring

View recent runs:
```bash
tail -50 /tmp/drift-detection.log
```

Watch live:
```bash
tail -f /tmp/drift-detection.log
```

## Troubleshooting

### Cron not running?

Check cron service:
```bash
# Git Bash on Windows uses Windows Task Scheduler, not cron
# Use Task Scheduler instead (see Windows section below)
```

### Script fails?

Test manually:
```bash
cd /c/Project/drift-detection-system
source venv/Scripts/activate
drift-detect --bucket drift-detection-drift-detection-dev-026bfe5b --sns-topic YOUR_ARN detect-all
```

## Windows Alternative: Task Scheduler

Since you're on Windows with Git Bash, use Task Scheduler instead:

### Create Batch File

Create `scripts/run-drift-detection.bat`:
```batch
@echo off
cd C:\Project\drift-detection-system
call venv\Scripts\activate.bat
drift-detect --bucket drift-detection-drift-detection-dev-026bfe5b --sns-topic YOUR_SNS_TOPIC_ARN detect-all >> C:\temp\drift-detection.log 2>&1
```

### Add to Task Scheduler

1. Open Task Scheduler (search in Start menu)
2. Click "Create Basic Task"
3. Name: "Drift Detection"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
6. Program: `C:\Project\drift-detection-system\scripts\run-drift-detection.bat`
7. Finish

### Test Task

Right-click task → Run

Check log:
```bash
type C:\temp\drift-detection.log
```

## Cost

**Running every 6 hours**:
- 4 runs/day × 30 days = 120 runs/month
- SNS emails (if drift detected): FREE (under 1,000/month)
- Total cost: **$0**

## Recommended Schedule

**Start with daily at 9 AM**, then adjust based on your needs:
- High-change environments: Every 6 hours
- Stable environments: Daily
- Production-critical: Every 2-4 hours
