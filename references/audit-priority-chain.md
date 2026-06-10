# Audit Priority Chain (from 2026-06-10 multi-dimensional review)

When handling a code-audit report with findings across multiple dimensions (security, correctness, style, architecture), apply this priority ordering:

## P0 — Scientific correctness (fix immediately)
- Geochemical formula errors (geometric vs arithmetic mean, NaN propagation)
- Calculation logic that silently drops or corrupts valid data
- Fix in single-file targeted patches, then re-run all tests

## P1 — Security + correctness (fix this week)
- HTML injection / XSS vectors: `html.escape()` on all user-supplied values in generated HTML
- `open()` without `encoding='utf-8'` (crashes on Windows systems with non-UTF8 locale)
- Truthiness traps on float values (`if val` skips 0.0 — use `is not None`)
- Partial-sum vs all-or-nothing logic drops valid data
- Cross-module value consistency (CHONDRITE Lu, TFe2O3 aliases)

## P2 — Security hardening + code quality
- `globals()` injection: add `valid_keys` whitelist to any code path that writes module globals from external data
- Path traversal: validate `category` against a whitelist, reject `..` / `/` in filenames, verify `os.path.realpath` prefix
- Stray string expressions (non-docstring module-level strings, lint-triggering)
- `matplotlib.use('Agg')` repeated in N modules — should be in one place only
- Hardcoded absolute paths in tools scripts

## P3 — Future iteration
- Type annotations on public API
- Docstring style unification
- Boundary-case tests
- Magic number extraction

## Validation chain
1. Patch each issue in isolation
2. Run `python3 -m pytest tests/ -v` (unit tests)
3. Run `python3 quick_validate.py` (diagram smoke test)
4. Commit per batch (P0 together, P1 together, P2 together)
