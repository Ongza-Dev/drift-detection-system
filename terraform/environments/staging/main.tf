# Staging Environment Configuration
terraform {
  backend "s3" {
    bucket         = "drift-detection-terraform-state-87cfc2b2"
    key            = "environments/staging/terraform.tfstate"
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
      Environment = "staging"
      ManagedBy   = "terraform"
    }
  }
}

# VPC for staging environment
module "vpc" {
  source = "../../modules/vpc"

  environment            = "staging"
  vpc_cidr              = "10.1.0.0/16"
  public_subnet_cidrs   = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnet_cidrs  = ["10.1.10.0/24", "10.1.20.0/24"]
}
