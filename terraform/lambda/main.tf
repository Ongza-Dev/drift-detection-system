terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ECR Repository
resource "aws_ecr_repository" "drift_detection" {
  name                 = "drift-detection-lambda"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "drift-detection-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy
resource "aws_iam_role_policy" "lambda_policy" {
  name = "drift-detection-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "rds:Describe*",
          "s3:*",
          "lambda:ListFunctions",
          "lambda:ListTags",
          "ecs:*"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = var.sns_topic_arn
      },
      {
        Effect   = "Allow"
        Action   = ["logs:*"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "drift_detection" {
  function_name = "drift-detection"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.drift_detection.repository_url}:latest"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      DRIFT_BUCKET  = var.drift_bucket
      SNS_TOPIC_ARN = var.sns_topic_arn
      ENVIRONMENTS  = var.environments
    }
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/drift-detection"
  retention_in_days = 7
}

# EventBridge Rule (daily at 9 AM UTC)
resource "aws_cloudwatch_event_rule" "daily_scan" {
  name                = "drift-detection-daily"
  schedule_expression = "cron(0 9 * * ? *)"
}

# EventBridge Target
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.daily_scan.name
  arn  = aws_lambda_function.drift_detection.arn
}

# Lambda Permission
resource "aws_lambda_permission" "allow_eventbridge" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.drift_detection.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_scan.arn
}
