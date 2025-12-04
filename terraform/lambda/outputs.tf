output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.drift_detection.repository_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.drift_detection.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.drift_detection.arn
}
