# Contributing to Drift Detection System

## Git Workflow

We follow **GitHub Flow** with protected branches and pull requests.

### Branch Structure

- `main` - Production-ready code, deployed to AWS Lambda
- `develop` - Integration branch for features
- `feature/*` - New features (e.g., `feature/add-alerting`)
- `bugfix/*` - Bug fixes (e.g., `bugfix/fix-cost-calculation`)
- `hotfix/*` - Emergency production fixes

### Development Workflow

#### 1. Create Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

#### 2. Make Changes

```bash
# Make your changes
# Run tests
make test

# Commit with descriptive message
git add .
git commit -m "Add feature: description"
```

#### 3. Push and Create PR

```bash
# Push feature branch
git push origin feature/your-feature-name

# Create Pull Request on GitHub:
# feature/your-feature-name → develop
```

#### 4. Code Review

- CI pipeline runs automatically (tests, linting, coverage)
- Request review from team members
- Address feedback
- Merge when approved

#### 5. Release to Production

```bash
# Merge develop → main via Pull Request
# This triggers automatic deployment to Lambda
```

## Commit Message Convention

Follow conventional commits:

```
feat: add SNS alerting for high-risk drift
fix: correct cost calculation for Lambda functions
docs: update deployment guide
test: add tests for risk scorer
refactor: simplify comparator logic
chore: update dependencies
```

## Code Quality Standards

### Before Committing

```bash
# Run tests
make test

# Format code
black src tests
isort src tests

# Lint
flake8 src tests
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pre-commit install
```

This automatically runs:
- Black (formatting)
- isort (import sorting)
- flake8 (linting)
- Trailing whitespace removal
- YAML validation

## Pull Request Guidelines

### PR Title

Use conventional commit format:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`

### PR Description

Use the template provided. Include:
- What changed and why
- How to test
- Screenshots (if UI changes)
- Breaking changes (if any)

### PR Checklist

- [ ] Tests pass (`make test`)
- [ ] Code formatted (`black`, `isort`)
- [ ] Linting passes (`flake8`)
- [ ] Documentation updated
- [ ] Coverage maintained (>80%)

## Testing

### Run Tests

```bash
# All tests
pytest tests -v

# With coverage
pytest tests -v --cov

# Specific test
pytest tests/test_risk_scorer.py -v
```

### Write Tests

- Unit tests for all new functions
- Integration tests for workflows
- Maintain >80% coverage

## Branch Protection Rules

### `main` branch

- Requires pull request
- Requires status checks (CI must pass)
- Requires code review
- No direct commits
- Triggers production deployment

### `develop` branch

- Requires pull request
- Requires status checks (CI must pass)
- No direct commits

## Release Process

1. Merge features to `develop` via PR
2. Test in develop environment
3. Create release PR: `develop` → `main`
4. Tag release: `git tag v1.0.0`
5. Automatic deployment to production Lambda

## Questions?

Open an issue or contact the maintainers.
