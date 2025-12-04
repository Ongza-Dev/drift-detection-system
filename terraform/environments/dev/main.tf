# Development Environment Configuration
terraform {
  backend "s3" {
    bucket         = "drift-detection-terraform-state-87cfc2b2"
    key            = "environments/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "drift-detection-terraform-locks"
    encrypt        = true
  }

  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "drift-detection-system"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

# VPC for development environment
module "vpc" {
  source = "../../modules/vpc"

  environment            = "dev"
  vpc_cidr              = "10.0.0.0/16"
  public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs  = ["10.0.10.0/24", "10.0.20.0/24"]
}

# S3 for drift detection data storage
module "s3" {
  source = "../../modules/s3"

  environment      = "dev"
  bucket_name      = "${var.project_name}-drift-detection-dev-${random_id.bucket_suffix.hex}"
  enable_versioning = true
  lifecycle_days   = 30  # Keep dev data for 30 days
}

# Random ID for unique bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}
