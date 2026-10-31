# BugRepro Detailed Workflow Reference

This reference details the step-by-step procedures expected of an autonomous agent when executing the BugRepro skill.

## Detailed Phase Breakdown

### Phase 1: Repository Understanding
1. Inspect directory layout using non-recursive or depth-limited directory listings.
2. Note location of source code (e.g. `src/`, `lib/`, or package directories) and tests (`tests/`, `test/`).
3. Check for dependency manifests:
   - Python: `pyproject.toml`, `requirements.txt`, `Pipfile`
   - Node: `package.json`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
4. Identify test runner and command syntax.
5. Capture clean Git baseline: `git status --porcelain`. Never commit or modify unrelated files.

### Phase 2: Bug Understanding
1. Extract bug title, summary, and reproduction steps.
2. Formulate explicit assertions:
   - What was the expected return value, side effect, or exception?
   - What was the observed return value or failure traceback?
3. Identify relevant environment preconditions (Python version, operating system, required packages).

### Phase 3: Bug Reproduction
1. Execute test suite against unmodified repository.
2. If targeted test exists, execute only that test to save time and reduce noise.
3. If no test reproduces the defect, author a minimal reproduction test file (e.g. `tests/repro_test.py`).
4. Execute with strict timeout (e.g. 60 seconds).
5. Record exit code and full standard error.
6. Checkpoint: Defect MUST be reproduced before progressing to patch generation.

### Phase 4: Root Cause Analysis
1. Inspect the call stack top-to-bottom.
2. Distinguish the symptom location from the defective logic location.
3. Inspect variable values and branching conditions around the failure point.
4. Record hypothesis with evidence citations.

### Phase 5: Patch Generation
1. Write minimal changes to fix the root cause.
2. Do not reformat adjacent lines or refactor unrelated code.
3. Verify that changes follow existing codebase conventions (style, typing, naming).
4. Produce a standard unified diff.

### Phase 6: Verification
1. Run syntax verification (`python -m py_compile` or `ast.parse`).
2. Run the targeted reproduction test: Must now pass with exit code 0.
3. Run existing regression test suite: Must not fail any previously passing test.
4. If tests fail: analyze failure, log retry, and adjust patch within allowed retry budget.

### Phase 7: Human Review
1. Display unified diff in formatted code block.
2. Display summary of test execution before and after patch.
3. Request explicit human confirmation before taking any action.

