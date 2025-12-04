"""Lambda handler for drift detection."""

import json
import os

from drift_detection.comparator import DriftComparator
from drift_detection.notifier import SNSNotifier
from drift_detection.reporter import DriftReporter
from drift_detection.scanner import AWSScanner
from drift_detection.storage import S3Storage


def handler(event, context):
    """Lambda handler for scheduled drift detection."""
    bucket = os.environ["DRIFT_BUCKET"]
    sns_topic = os.environ["SNS_TOPIC_ARN"]
    region = os.environ.get("AWS_REGION", "us-east-1")
    environments = os.environ.get("ENVIRONMENTS", "dev,staging,prod").split(",")

    scanner = AWSScanner(region=region)
    storage = S3Storage(bucket_name=bucket, region=region)
    comparator = DriftComparator()
    reporter = DriftReporter()
    notifier = SNSNotifier(region=region)

    results = []

    for env in environments:
        print(f"Scanning environment: {env}")

        baseline_data = storage.load_baseline(env)
        if not baseline_data:
            print(f"No baseline found for {env}, skipping")
            results.append({"environment": env, "status": "no_baseline"})
            continue

        current_data = scanner.scan_environment(env)
        drift_result = comparator.compare(baseline_data, current_data)
        report = reporter.generate_report(drift_result)
        storage.save_report(env, report)

        if drift_result["drift_detected"]:
            message_id = notifier.send_alert(report, sns_topic, min_risk="high")
            results.append(
                {
                    "environment": env,
                    "status": "drift_detected",
                    "risk": report["risk_assessment"]["overall_risk"],
                    "alert_sent": message_id is not None,
                }
            )
        else:
            results.append({"environment": env, "status": "no_drift"})

    return {"statusCode": 200, "body": json.dumps({"results": results})}
