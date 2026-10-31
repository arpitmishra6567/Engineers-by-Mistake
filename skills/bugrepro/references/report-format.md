# BugRepro Standard Report Format

Every repair workflow must generate a standardized report in GitHub Flavored Markdown adhering to the exact schema below.

```markdown
# Repair Report

## Issue Summary
- **Title**: Brief defect summary
- **Expected Behavior**: What the software was supposed to do
- **Actual Behavior**: What the software actually did
- **Details**: Full issue description or context

## Repository Analysis
- **Files Tracked**: Total number of source files analyzed
- **Languages**: Languages detected
- **Test Framework**: Test framework detected (e.g. pytest)

## Reproduction Evidence
- **Outcome**: REPRODUCED | NOT_REPRODUCED | BLOCKED
- **Command**: Exact test command executed
- **Exit Code**: Command return code
- **Duration**: Elapsed execution time
- **Evidence**: Specific error message, assertion, or stack trace observed

## Root Cause
- **File**: Primary file containing the defect
- **Function/Component**: Function or class name
- **Uncertainty**: LOW | MEDIUM | HIGH
- **Explanation**: Technical reasoning explaining why the failure occurs
- **Evidence**: Execution trace or code evidence supporting diagnosis

## Files Modified
- Path to each modified file

## Patch Summary
Description of the patch changes and the complete unified diff:
```diff
--- a/file.py
+++ b/file.py
@@ ... @@
```

## Verification Results
- **Verification Outcome**: PASSED | FAILED
- **Syntax Check**: Valid | Invalid
- **Command Executed**: Regression test command
- **Exit Code**: Return code of verification test
- **Tests Passed**: Comma-separated list of passed test suites
- **Tests Failed**: Comma-separated list of failed test suites

## Remaining Risks
- Known limitations, untested edge cases, or runtime considerations

## Status
Must be exactly one of:
- VERIFIED
- PATCH_GENERATED_UNVERIFIED
- VALIDATION_FAILED
- NOT_REPRODUCED
- BLOCKED
```

### Status Value Definitions
- `VERIFIED`: The defect was reproduced, a patch was applied, and all relevant verification tests passed (exit code 0).
- `PATCH_GENERATED_UNVERIFIED`: A patch was produced but verification was skipped or untested.
- `VALIDATION_FAILED`: A patch was generated, but tests failed or syntax errors occurred.
- `NOT_REPRODUCED`: The bug could not be triggered or reproduced by the test harness.
- `BLOCKED`: The task was halted due to security violation, timeouts, or missing dependencies.

