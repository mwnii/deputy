# Code Quality Skill

**Category:** development

## Linting Protocol

Every agent that writes code MUST run linters before declaring task complete.

### Step 1: Ruff Check (errors + warnings)
```bash
ruff check <file>
```
Fix ALL errors. Common rules:
- E: pycodestyle errors (whitespace, line length)
- F: pyflakes (unused imports, undefined names, bare except)
- I: isort (import sorting)
- N: pep8-naming (naming conventions)
- W: pycodestyle warnings
- UP: pyupgrade (modern Python syntax)

### Step 2: Ruff Format (auto-format)
```bash
ruff format <file>
```
This auto-formats code to match project style (Black-compatible).

### Step 3: Pyright (type checking)
```bash
pyright <file>
```
Catches type errors, missing imports, incorrect annotations.
Only available if pyright is installed.

### Step 4: Auto-fix safe issues
```bash
ruff check --fix <file>    # Auto-fix safe issues
ruff format <file>         # Auto-format
```

## Evaluation Criteria
- **PASS:** 0 lint errors after fixes
- **PASS (with note):** Lint errors found and fixed during task
- **FAIL:** Lint errors left unfixed

## Pre-commit Check
```bash
ruff check . && ruff format --check .
```

## Installation
```bash
pip install ruff          # Python linter + formatter (fast, Rust-based)
pip install pyright       # Python type checker
```

## Project Configuration
Lint rules are configured in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```
