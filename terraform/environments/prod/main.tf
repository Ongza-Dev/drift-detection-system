# Production Environment Configuration
terraform {
  backend "s3" {
    bucket         = "drift-detection-terraform-state-87cfc2b2"
    key            = "environments/prod/terraform.tfstate"
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
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "drift-detection-system"
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

# VPC for production environment
module "vpc" {
  source = "../../modules/vpc"

  environment            = "prod"
  vpc_cidr              = "10.2.0.0/16"
  public_subnet_cidrs   = ["10.2.1.0/24", "10.2.2.0/24"]
  private_subnet_cidrs  = ["10.2.10.0/24", "10.2.20.0/24"]
}
