# Design: Task 1.10 – Add Development Tooling (Linting, Formatting, Requirements)

## Overview

Set up project dependencies, linting (`ruff`), formatting (`black`), and testing (`pytest-django`). Use `pyproject.toml` as the single source for tool configuration.

## Dependencies

- Task 1.1

## Detailed Design

### Files Created/Modified

| File | Action |
|------|--------|
| `requirements.txt` | Complete dependency list |
| `requirements-dev.txt` | Dev-only dependencies |
| `pyproject.toml` | Tool configuration |

### Step-by-Step Implementation

1. **Create `requirements.txt`** (production dependencies):
   ```
   Django>=5.1,<5.2
   django-environ>=0.11
   djangorestframework>=3.15
   psycopg2-binary>=2.9
   azure-cognitiveservices-speech>=1.37
   openai>=1.30
   gunicorn>=22.0
   whitenoise>=6.6
   ```

2. **Create `requirements-dev.txt`**:
   ```
   -r requirements.txt
   pytest>=8.0
   pytest-django>=4.8
   pytest-cov>=5.0
   ruff>=0.4
   black>=24.0
   factory-boy>=3.3
   ```

3. **Create `pyproject.toml`**:
   ```toml
   [project]
   name = "phonics-app"
   version = "0.1.0"
   requires-python = ">=3.11"

   [tool.pytest.ini_options]
   DJANGO_SETTINGS_MODULE = "config.settings.dev"
   python_files = ["tests.py", "test_*.py", "*_tests.py"]
   python_paths = ["."]
   addopts = [
       "--strict-markers",
       "--tb=short",
       "-q",
   ]
   testpaths = ["apps"]

   [tool.ruff]
   target-version = "py311"
   line-length = 120
   src = ["apps", "config"]

   [tool.ruff.lint]
   select = [
       "E",    # pycodestyle errors
       "W",    # pycodestyle warnings
       "F",    # pyflakes
       "I",    # isort
       "B",    # flake8-bugbear
       "UP",   # pyupgrade
       "DJ",   # flake8-django
   ]
   ignore = [
       "E501",  # line too long (handled by formatter)
   ]

   [tool.ruff.lint.isort]
   known-first-party = ["apps", "config"]

   [tool.black]
   line-length = 120
   target-version = ["py311"]

   [tool.coverage.run]
   source = ["apps"]
   omit = ["*/migrations/*", "*/tests/*"]

   [tool.coverage.report]
   show_missing = true
   fail_under = 70
   ```

4. **Install dev dependencies**:
   ```powershell
   pip install -r requirements-dev.txt
   ```

### Tool Usage

```powershell
# Lint
ruff check .

# Auto-fix lint issues
ruff check . --fix

# Format
black .

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## Acceptance Criteria

- [ ] `pip install -r requirements-dev.txt` succeeds
- [ ] `ruff check .` runs cleanly (no errors)
- [ ] `black --check .` reports no formatting issues
- [ ] `pytest` discovers test directories (0 tests initially is fine)
- [ ] All project dependencies pinned with minimum versions

## Test Strategy

- Manual: Run `pip install -r requirements-dev.txt && pytest && ruff check .`
