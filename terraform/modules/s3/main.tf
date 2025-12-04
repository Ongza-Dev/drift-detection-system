# S3 Bucket for Drift Detection Storage
resource "aws_s3_bucket" "drift_detection" {
  bucket = var.bucket_name

  tags = {
    Name        = "${var.environment}-drift-detection-storage"
    Environment = var.environment
    Purpose     = "drift-detection-data"
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "drift_detection" {
  bucket = aws_s3_bucket.drift_detection.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "drift_detection" {
  bucket = aws_s3_bucket.drift_detection.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "drift_detection" {
  bucket = aws_s3_bucket.drift_detection.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "drift_detection" {
  depends_on = [aws_s3_bucket_versioning.drift_detection]
  bucket     = aws_s3_bucket.drift_detection.id

  rule {
    id     = "cleanup_old_scans"
    status = "Enabled"

    filter {
      prefix = "scans/"
    }

    expiration {
      days = var.lifecycle_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "cleanup_old_reports"
    status = "Enabled"

    filter {
      prefix = "reports/"
    }

    expiration {
      days = var.lifecycle_days * 2  # Keep reports longer
    }
  }
}
