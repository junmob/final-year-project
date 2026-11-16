# 0001: Keeping collector tests out of the real data directory

| Field | Value |
|---|---|
| Date | 2026-11-17 |
| Module | Collector tests (`tests/test_collect_gtfs_rt.py`) |
| Ticket / PR | T02 / #1 |
| Versions | Single version; the issue was avoided before any test code was written. Commits `016915d`, `51b50d3`, `d915628`, `a63c6dd`, `4d29da0` |
| Provenance | Engineering issue (no data-source ID). The fix was suggested by an external AI assistant (claude.ai) while the student was asking how `monkeypatch` works; it was adopted before coding and the student's understanding was then checked with four questions |
| Hint levels used | none |
| Authorship | Drafted by Claude from the student's debrief; reviewed by the student |

## Context
`ingestion/collect_gtfs_rt.py` has run on the collector VM since October with no automated tests. T02 added pytest unit tests for `write_atomic`, `classify`, `write_health` and `fetch_slot`. Two constraints applied: tests must not call the network (the real API allows four requests per minute and the VM collector uses all of them), and tests may create files only under pytest's `tmp_path`.

## The trap
The collector works out its output directories once, at module level:

```python
BRONZE_DIR = Path(os.environ.get("BRONZE_DIR", ROOT / "data" / "bronze"))
RT_DIR = BRONZE_DIR / "gtfs_rt"
HEALTH_DIR = BRONZE_DIR / "_health"
```

These lines run when the test file executes `import collect_gtfs_rt`, and Python caches the module in `sys.modules`, so they never run again. A natural first test sets the environment variable with `monkeypatch.setenv("BRONZE_DIR", tmp_path)`, but by then the three `Path` objects already exist and do not change. On the student's laptop `BRONZE_DIR` is unset, so `fetch_slot` would write `.pb` files and health logs into `<repo>/data/bronze/`. That directory is in `.gitignore`, so `git status` stays clean and every test still passes: the pollution is silent.

Before issuing the ticket, Claude reproduced this in a scratch clone of the repository with a `setenv`-only test: the test passed and `git status --ignored --short` gained the line `!! data/bronze/`.

## What the student planned and why
- **First prediction (9 November).** Asked which files the tests would create and where, the student listed paths under `/home/junmob/fyp-data/bronze/`, without yet working out where the default path resolves on the laptop or how to redirect it.
- **Revised prediction (11 November), before any test code.** While asking another AI assistant how `monkeypatch` works, the student was told about the import-time trap. The revised plan used `monkeypatch.setattr` to replace all three module attributes (`BRONZE_DIR`, `RT_DIR`, `HEALTH_DIR`) with directories under `tmp_path`.
- **Understanding check (11 November).** Asked closed-book, the student explained that importing the module runs its top-level code once and caches it; that `setenv` after import does not change the stored paths; and that replacing only `BRONZE_DIR` would fail in a specific way: `write_atomic` (line 104) writes the `.pb` into the old `RT_DIR` first, then `path.relative_to(BRONZE_DIR)` (line 107) raises `ValueError`, which none of the three `except` clauses catch. The test errors, no health record is written, and a stray file is left behind. The student also named the design alternative: pass paths into functions as parameters (dependency injection), as `write_atomic` already does.
- **Why the fix works (debrief).** `fetch_slot` and `write_health` look up `RT_DIR`, `BRONZE_DIR` and `HEALTH_DIR` in the module at the moment they are called, not when they are defined. `setattr` rebinds those names before the call, and `monkeypatch` restores them after each test.

## Implementation
- The fixture `bronze(tmp_path, monkeypatch)` replaces the three attributes and returns `tmp_path`. All three `fetch_slot` tests use it; the `write_health` test replaces `HEALTH_DIR`; the `write_atomic` tests pass a `tmp_path` path directly.
- `collect_gtfs_rt.session.get` is replaced with small fake functions: an HTTP 200 response with a valid GTFS Realtime message, an HTTP 429 response, and one that raises `requests.Timeout`. The fake responses define only `status_code` and `content`, the two attributes `fetch_slot` reads.

## Evidence
- `pytest -q`: 12 passed. Each test also passes when run on its own (`pytest -q -k <name>`).
- Isolation check, recorded in PR #1: `git status --ignored --short` before and after `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider` is identical (`SAME`). The two settings stop Python and pytest writing their own cache directories, so any new path would have come from the tests.
- `git diff main -- ingestion/` is empty.
- Prediction 1 (the `.pb` path for slot `1792684815`, `date=2026-10-23/hour=00/20261022T160015Z.pb`) matched the test result.

## Secondary findings from review
Review found two assertions that could never fail:
1. A `fetch_slot` timeout test that defined a fake function but never called `fetch_slot` and had no `assert`. It "passed" while checking nothing.
2. `assert not (bronze / PB_REL).exists() == []`. Python evaluates this as `not (exists() == [])`; a boolean never equals an empty list, so the expression is `True` whether or not the file exists. It was replaced in `4d29da0` by `assert list(bronze.rglob("*.pb")) == []`, which also catches a `.pb` written to any directory, not just the expected one.

## Lessons
- Module-level code runs at import time. Tests must replace what a module has already computed (`monkeypatch.setattr`), not the inputs it read earlier (`setenv`). Code written from S1 onwards takes paths as parameters, so tests do not need to patch module state.
- A passing test is evidence only if it could fail. Check that every test has an assertion, and that each assertion would fail for at least one plausible wrong implementation. For example, `write_health` is tested with two records, because a single record cannot tell append mode from overwrite mode.
- Assertions that something exists should be specific (exact path and content); assertions that something does not exist should be broad (nothing anywhere under `tmp_path`).
- The same import-time behaviour matters for Airflow: the scheduler re-parses DAG files every few tens of seconds by executing their top-level code, so heavy work (reading large files, opening database connections) belongs inside task functions.

## References
- Design baseline v0.5, §14.1 (DataOps) and §14.2 (testing strategy, unit tests).
- pytest documentation: `tmp_path` and `monkeypatch` (https://docs.pytest.org/en/stable/how-to/tmp_path.html, https://docs.pytest.org/en/stable/how-to/monkeypatch.html).
