# Drift Detection Application

Production-ready drift detection system for multi-environment AWS infrastructure.

## Architecture

### Core Modules

- **scanner.py**: Scans AWS resources (VPC, EC2, RDS, S3, Lambda, ECS) by environment tag
- **storage.py**: Manages S3 storage for baselines, scans, and reports
- **comparator.py**: Detects drift using DeepDiff for configuration comparison
- **reporter.py**: Generates human-readable drift reports with recommendations
- **cli.py**: Command-line interface with structured logging

### Design Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Components are loosely coupled
- **Type Safety**: Full type hints for better IDE support and error detection
- **Error Handling**: Graceful degradation with proper logging
- **Testability**: Mocked AWS services for unit testing

## Usage

### Install

```bash
pip install -e .
```

### Commands

```bash
# Set baseline for an environment
drift-detect --bucket my-bucket baseline dev

# Scan current infrastructure
drift-detect --bucket my-bucket scan dev

# Detect drift (compare current to baseline)
drift-detect --bucket my-bucket detect dev

# Detect drift across all environments
drift-detect --bucket my-bucket detect-all
```

### Environment Variables

```bash
AWS_REGION=us-east-1
AWS_PROFILE=default
```

## Development

### Run Tests

```bash
make test
```

### Code Quality

```bash
make lint    # Run flake8
make format  # Run black and isort
```

### Pre-commit Hooks

```bash
pre-commit install
```

## Storage Structure

```
s3://bucket-name/
├── baselines/
│   ├── dev/baseline.json
│   ├── staging/baseline.json
│   └── prod/baseline.json
├── scans/
│   ├── dev/20240101-120000.json
│   └── ...
└── reports/
    ├── dev/20240101-120000.json
    └── ...
```

## Testing Strategy

- **Unit Tests**: Mock AWS services using moto/unittest.mock
- **Integration Tests**: Test against localstack (future)
- **Coverage Target**: >80%
