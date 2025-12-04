"""SNS notification for drift alerts."""

import logging
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SNSNotifier:
    """Sends drift alerts via AWS SNS."""

    def __init__(self, region: str = "us-east-1"):
        self.sns = boto3.client("sns", region_name=region)

    def send_alert(
        self, report: Dict[str, Any], topic_arn: str, min_risk: str = "high"
    ) -> Optional[str]:
        """Send SNS alert for drift if risk threshold met."""
        risk = report["risk_assessment"]["overall_risk"]
        risk_levels = ["info", "low", "medium", "high", "critical"]

        if risk_levels.index(risk) < risk_levels.index(min_risk):
            logger.info(f"Skipping alert - risk {risk} below threshold {min_risk}")
            return None

        subject = self._format_subject(report)
        message = self._format_message(report)

        try:
            response = self.sns.publish(
                TopicArn=topic_arn, Subject=subject, Message=message
            )
            logger.info(f"SNS alert sent: {response['MessageId']}")
            return response["MessageId"]
        except ClientError as e:
            logger.error(f"Failed to send SNS alert: {e}")
            return None

    def _format_subject(self, report: Dict[str, Any]) -> str:
        """Format alert subject line."""
        risk = report["risk_assessment"]["overall_risk"].upper()
        env = report["environment"]
        emoji = {"critical": "🚨", "high": "⚠️", "medium": "⚠"}.get(risk.lower(), "ℹ️")
        return f"{emoji} {risk} Drift Detected: {env}"

    def _format_message(self, report: Dict[str, Any]) -> str:
        """Format alert message body."""
        lines = [
            f"Environment: {report['environment']}",
            f"Risk Level: {report['risk_assessment']['overall_risk'].upper()}",
            "",
            f"Summary: {report['summary']}",
            "",
        ]

        # Risk breakdown
        dist = report["risk_assessment"]["risk_distribution"]
        risk_counts = [
            f"  - {level.capitalize()}: {count}"
            for level, count in dist.items()
            if count > 0 and level != "info"
        ]
        if risk_counts:
            lines.append("Risk Breakdown:")
            lines.extend(risk_counts)
            lines.append("")

        # Cost impact
        cost = report["cost_impact"]
        if cost["monthly_impact"] != 0:
            sign = "+" if cost["monthly_impact"] > 0 else ""
            lines.append(
                f"Cost Impact: {sign}${cost['monthly_impact']:.2f}/month "
                f"({cost['impact_percentage']:+.1f}%)"
            )
            lines.append("")

        # Top recommendations
        lines.append("Recommendations:")
        for rec in report["recommendations"][:3]:
            lines.append(f"  • {rec}")

        return "\n".join(lines)
