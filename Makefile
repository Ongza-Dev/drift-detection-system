.PHONY: help test build deploy clean

help:
	@echo "Drift Detection System - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  test          - Run tests"
	@echo "  build         - Build Docker image locally"
	@echo "  deploy-infra  - Deploy infrastructure with Terraform"
	@echo "  deploy-lambda - Build and deploy Lambda function"
	@echo "  clean         - Clean up local artifacts"

test:
	pytest tests -v --cov

build:
	docker build -t drift-detection:latest -f lambda/Dockerfile .

deploy-infra:
	cd terraform/lambda && \
	terraform init && \
	terraform plan && \
	terraform apply

deploy-lambda:
	@echo "Building and pushing to ECR..."
	$(eval ECR_URL := $(shell cd terraform/lambda && terraform output -raw ecr_repository_url))
	docker build -t $(ECR_URL):latest -f lambda/Dockerfile .
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(ECR_URL)
	docker push $(ECR_URL):latest
	aws lambda update-function-code --function-name drift-detection --image-uri $(ECR_URL):latest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
