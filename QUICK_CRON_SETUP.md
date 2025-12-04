# Quick Cron Setup (Windows)

## 1. Edit the Batch File

Open `scripts/run-drift-detection.bat` and replace:
```batch
set SNS_TOPIC=YOUR_SNS_TOPIC_ARN
```

With your actual SNS topic ARN:
```batch
set SNS_TOPIC=arn:aws:sns:us-east-1:123456789012:drift-alerts
```

## 2. Test It

Run in Git Bash or Command Prompt:
```bash
scripts\run-drift-detection.bat
```

Check the log:
```bash
type C:\temp\drift-detection.log
```

## 3. Add to Windows Task Scheduler

### Option A: GUI (Easy)

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click "Create Basic Task" (right panel)
3. Name: `Drift Detection`
4. Trigger: `Daily`
5. Time: `9:00 AM`
6. Action: `Start a program`
7. Program: `C:\Project\drift-detection-system\scripts\run-drift-detection.bat`
8. Click Finish

### Option B: Command Line (Fast)

Run in Command Prompt as Administrator:
```cmd
schtasks /create /tn "DriftDetection" /tr "C:\Project\drift-detection-system\scripts\run-drift-detection.bat" /sc daily /st 09:00
```

## 4. Test the Scheduled Task

Right-click "Drift Detection" task → Run

Check log:
```bash
type C:\temp\drift-detection.log
```

## 5. Done!

Your system now automatically:
- ✅ Scans infrastructure daily at 9 AM
- ✅ Detects drift across all environments
- ✅ Sends email alerts for HIGH/CRITICAL risks
- ✅ Logs all activity to `C:\temp\drift-detection.log`

## Change Schedule

### Every 6 hours
```cmd
schtasks /create /tn "DriftDetection" /tr "C:\Project\drift-detection-system\scripts\run-drift-detection.bat" /sc hourly /mo 6
```

### Twice daily (9 AM and 9 PM)
Create two tasks or use GUI to add multiple triggers.

## View Logs

```bash
# Last 50 lines
tail -50 /c/temp/drift-detection.log

# Watch live
tail -f /c/temp/drift-detection.log
```

## Disable/Enable

```cmd
# Disable
schtasks /change /tn "DriftDetection" /disable

# Enable
schtasks /change /tn "DriftDetection" /enable

# Delete
schtasks /delete /tn "DriftDetection"
```
