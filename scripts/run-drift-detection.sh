#!/bin/bash
# Drift Detection Cron Script

# Configuration
PROJECT_DIR="/c/Project/drift-detection-system"
VENV_DIR="$PROJECT_DIR/venv"
BUCKET="drift-detection-drift-detection-dev-026bfe5b"
SNS_TOPIC="YOUR_SNS_TOPIC_ARN"  # Replace with your actual SNS topic ARN
LOG_FILE="/tmp/drift-detection.log"

# Activate virtual environment
source "$VENV_DIR/Scripts/activate"

# Set AWS region (if needed)
export AWS_REGION=us-east-1

# Run drift detection
echo "=== Drift Detection Run: $(date) ===" >> "$LOG_FILE"
drift-detect --bucket "$BUCKET" --sns-topic "$SNS_TOPIC" detect-all >> "$LOG_FILE" 2>&1

# Exit status
if [ $? -eq 0 ]; then
    echo "✓ Drift detection completed successfully" >> "$LOG_FILE"
else
    echo "✗ Drift detection failed" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
