# Contributing to slopcheck

Thank you for your interest in contributing! Please follow these guidelines to keep the codebase clean and reliable.

## Development Workflow

1. **Branch-per-Feature:** Create a new branch for every feature or bug fix. Do not commit directly to the `main` branch.
   ```bash
   git checkout -b my-new-feature
   ```
2. **Pull Request Required:** All changes must be submitted via a Pull Request (PR). Direct pushes to `main` are restricted.
3. **Tests Must Pass:** Ensure all tests and linting checks pass locally before opening a PR.

## Running Tests

To set up your environment and run tests locally:

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Run code formatter and linter check
ruff check .

# Run pytest suite
python -m pytest
```
