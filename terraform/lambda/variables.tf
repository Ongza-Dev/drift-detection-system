variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "drift_bucket" {
  description = "S3 bucket for drift detection data"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  type        = string
}

variable "environments" {
  description = "Comma-separated list of environments to scan"
  type        = string
  default     = "dev,staging,prod"
}
