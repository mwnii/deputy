# Code Review Skill

**Category:** development

## Code Review Protocol

When reviewing code (own or others'), follow this checklist:

### Correctness
- [ ] Code does what it claims to do
- [ ] Edge cases are handled
- [ ] Error handling is present (try/except, retries)
- [ ] No hardcoded credentials or secrets

### Quality
- [ ] Passes `ruff check` with 0 errors
- [ ] Passes `ruff format` (auto-formatted)
- [ ] Passes `pyright` type check (if available)
- [ ] Functions are focused (single responsibility)
- [ ] Variable names are descriptive
- [ ] No dead code or unused imports

### Security
- [ ] No secrets in code (use env vars)
- [ ] Input validation present
- [ ] No SQL injection, XSS, or similar vulnerabilities
- [ ] API keys never logged or printed

### Performance
- [ ] No obvious performance issues
- [ ] Database queries are efficient
- [ ] No unnecessary loops or computations

### Documentation
- [ ] Functions have docstrings
- [ ] Complex logic has comments
- [ ] README updated if public-facing

## Review Output Format
```
## Code Review: [filename]

**Status:** APPROVED / CHANGES REQUESTED

### Issues Found
1. [severity] [description] — line [N]

### Recommendations
- [suggestion]

### Lint Results
- ruff check: [pass/fail]
- ruff format: [pass/fail]
- pyright: [pass/fail]
```

## Severity Levels
- **CRITICAL:** Security vulnerability, data loss risk
- **ERROR:** Bug, incorrect behavior
- **WARNING:** Code smell, potential issue
- **STYLE:** Formatting, naming, minor improvement
