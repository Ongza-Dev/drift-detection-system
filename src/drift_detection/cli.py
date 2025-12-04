"""Command-line interface for drift detection system."""

import sys

import click
import structlog

from drift_detection.comparator import DriftComparator
from drift_detection.notifier import SNSNotifier
from drift_detection.reporter import DriftReporter
from drift_detection.scanner import AWSScanner
from drift_detection.storage import S3Storage

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ]
)
logger = structlog.get_logger()


@click.group()
@click.option("--region", default="us-east-1", help="AWS region")
@click.option("--bucket", required=True, help="S3 bucket for storage")
@click.option("--sns-topic", default=None, help="SNS topic ARN for alerts")
@click.pass_context
def cli(ctx: click.Context, region: str, bucket: str, sns_topic: str) -> None:
    """Multi-environment drift detection system."""
    ctx.ensure_object(dict)
    ctx.obj["region"] = region
    ctx.obj["bucket"] = bucket
    ctx.obj["sns_topic"] = sns_topic
    ctx.obj["scanner"] = AWSScanner(region=region)
    ctx.obj["storage"] = S3Storage(bucket_name=bucket, region=region)
    ctx.obj["comparator"] = DriftComparator()
    ctx.obj["reporter"] = DriftReporter()


@cli.command()
@click.argument("environment")
@click.pass_context
def scan(ctx: click.Context, environment: str) -> None:
    """Scan AWS infrastructure for an environment."""
    logger.info("scan_started", environment=environment)

    scanner = ctx.obj["scanner"]
    storage = ctx.obj["storage"]

    scan_data = scanner.scan_environment(environment)
    key = storage.save_scan(environment, scan_data)

    logger.info("scan_completed", environment=environment, s3_key=key)
    click.echo(f"✓ Scan completed: {key}")


@cli.command()
@click.argument("environment")
@click.pass_context
def baseline(ctx: click.Context, environment: str) -> None:
    """Set current state as baseline for an environment."""
    logger.info("baseline_creation_started", environment=environment)

    scanner = ctx.obj["scanner"]
    storage = ctx.obj["storage"]

    scan_data = scanner.scan_environment(environment)
    key = storage.save_baseline(environment, scan_data)

    logger.info("baseline_created", environment=environment, s3_key=key)
    click.echo(f"✓ Baseline created: {key}")


@cli.command()
@click.argument("environment")
@click.pass_context
def detect(ctx: click.Context, environment: str) -> None:
    """Detect drift by comparing current state to baseline."""
    logger.info("drift_detection_started", environment=environment)

    scanner = ctx.obj["scanner"]
    storage = ctx.obj["storage"]
    comparator = ctx.obj["comparator"]
    reporter = ctx.obj["reporter"]

    # Load baseline
    baseline_data = storage.load_baseline(environment)
    if not baseline_data:
        logger.error("baseline_not_found", environment=environment)
        msg = f"✗ No baseline found for {environment}. Run 'baseline' first."
        click.echo(msg)
        sys.exit(1)

    # Scan current state
    current_data = scanner.scan_environment(environment)

    # Compare and detect drift
    drift_result = comparator.compare(baseline_data, current_data)

    # Generate report
    report = reporter.generate_report(drift_result)
    key = storage.save_report(environment, report)

    # Send SNS alert if configured
    sns_topic = ctx.obj.get("sns_topic")
    if sns_topic and drift_result["drift_detected"]:
        notifier = SNSNotifier(region=ctx.obj["region"])
        message_id = notifier.send_alert(report, sns_topic, min_risk="high")
        if message_id:
            logger.info("sns_alert_sent", message_id=message_id)

    # Display results
    if drift_result["drift_detected"]:
        risk = report["risk_assessment"]["overall_risk"]
        risk_emoji = _get_risk_emoji(risk)

        logger.warning("drift_detected", environment=environment, risk=risk)
        click.echo(f"{risk_emoji} Drift detected in {environment}")
        click.echo(f"  {report['summary']}")

        # Show risk distribution
        dist = report["risk_assessment"]["risk_distribution"]
        risk_counts = [
            f"{count} {level}"
            for level, count in dist.items()
            if count > 0 and level != "info"
        ]
        if risk_counts:
            click.echo(f"  Risk breakdown: {', '.join(risk_counts)}")

        # Show cost impact
        cost = report["cost_impact"]
        if cost["monthly_impact"] != 0:
            impact_sign = "+" if cost["monthly_impact"] > 0 else ""
            click.echo(
                f"  💰 Cost Impact: {impact_sign}"
                f"${cost['monthly_impact']:.2f}/month "
                f"({cost['impact_percentage']:+.1f}%)"
            )

        # Show top recommendations
        click.echo("\n  Recommendations:")
        for rec in report["recommendations"][:3]:
            click.echo(f"    • {rec}")

        # Show SNS alert status
        if sns_topic:
            click.echo("\n  📧 Alert sent to SNS topic")
    else:
        logger.info("no_drift", environment=environment)
        click.echo(f"✓ No drift detected in {environment}")

    click.echo(f"\n  Report saved: {key}")


@cli.command()
@click.pass_context
def detect_all(ctx: click.Context) -> None:
    """Detect drift across all environments."""
    environments = ["dev", "staging", "prod"]

    for env in environments:
        click.echo(f"\n{'='*50}")
        click.echo(f"Environment: {env}")
        click.echo(f"{'='*50}")
        ctx.invoke(detect, environment=env)


def _get_risk_emoji(risk_level: str) -> str:
    """Get emoji for risk level."""
    emojis = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "⚠",
        "low": "ℹ️",
        "info": "✓",
    }
    return emojis.get(risk_level, "⚠")


def main() -> None:
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
