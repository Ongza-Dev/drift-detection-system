# Git Workflow Setup Guide

## Initial Setup (One Time)

### 1. Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/drift-detection-system.git

# Push main branch
git branch -M main
git push -u origin main
```

### 2. Create Develop Branch

```bash
# Create and push develop branch
git checkout -b develop
git push -u origin develop
```

### 3. Configure Branch Protection (GitHub Web)

#### Protect `main` branch:
1. Go to Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass (select "test" job)
   - ✅ Require branches to be up to date
   - ✅ Do not allow bypassing the above settings
4. Save

#### Protect `develop` branch:
1. Add another rule for `develop`
2. Same settings as main

### 4. Set Default Branch

1. Settings → Branches → Default branch
2. Change to `develop`
3. Update

### 5. Add GitHub Secrets

Settings → Secrets and variables → Actions → New repository secret:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Daily Workflow

### Working on New Feature

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/add-new-feature

# 3. Make changes and commit
git add .
git commit -m "feat: add new feature description"

# 4. Push feature branch
git push origin feature/add-new-feature

# 5. Create Pull Request on GitHub
# feature/add-new-feature → develop

# 6. Wait for CI to pass and get review

# 7. Merge PR on GitHub
```

### Releasing to Production

```bash
# 1. Create release PR on GitHub
# develop → main

# 2. Review changes

# 3. Merge PR
# This automatically deploys to Lambda

# 4. Tag release
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Hotfix (Emergency Production Fix)

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Fix and commit
git add .
git commit -m "fix: critical bug description"

# 3. Push and create PR
git push origin hotfix/critical-bug-fix

# Create PR: hotfix/critical-bug-fix → main

# 4. After merge, sync back to develop
git checkout develop
git pull origin develop
git merge main
git push origin develop
```

## CI/CD Pipeline

### On Pull Request
- Runs linting (black, isort, flake8)
- Runs tests with coverage
- Must pass before merge

### On Push to `main`
- Runs full test suite
- Builds Docker image
- Pushes to ECR
- Updates Lambda function
- Deploys to production

## Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Emergency fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Test improvements

## Example Workflow

```bash
# Feature development
git checkout develop
git checkout -b feature/add-slack-integration
# ... make changes ...
git commit -m "feat: add Slack webhook integration"
git push origin feature/add-slack-integration
# Create PR → develop → Merge

# Release to production
# Create PR: develop → main → Merge
# Automatic deployment happens

# Tag release
git tag v1.1.0
git push origin v1.1.0
```

## Troubleshooting

### CI Fails
```bash
# Run locally first
make test
black --check src tests
isort --check-only src tests
flake8 src tests
```

### Merge Conflicts
```bash
# Update your branch with latest develop
git checkout feature/your-feature
git fetch origin
git merge origin/develop
# Resolve conflicts
git commit
git push
```

### Revert Bad Deployment
```bash
# Find previous working commit
git log

# Revert on main
git checkout main
git revert <bad-commit-sha>
git push origin main
# This triggers redeployment
```
