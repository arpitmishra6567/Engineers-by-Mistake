"""Unit tests for bug report and issue parser."""

from repairforge.investigation.issue_parser import IssueParser


def test_issue_parser_markdown():
    """Verify IssueParser parses markdown headings into structured fields."""
    raw_md = """# Division by zero in calc

## Expected Behavior
The function should return 0 when list is empty.

## Actual Behavior
Raises ZeroDivisionError on line 12.

## Error Message & Stack Trace
```text
ZeroDivisionError: division by zero
  File "calc.py", line 12, in calc
```

## Reproduction Command
```bash
python -m pytest test_calc.py
```
"""
    bug_report = IssueParser.parse(raw_md)
    assert bug_report.title == "Division by zero in calc"
    assert "return 0" in bug_report.expected_behavior
    assert "ZeroDivisionError" in bug_report.actual_behavior
    assert "ZeroDivisionError: division by zero" in (bug_report.error_message or "")
    assert bug_report.reproduction_command == "python -m pytest test_calc.py"


def test_issue_parser_fallback_unstructured():
    """Verify IssueParser handles raw unstructured error text gracefully."""
    raw_text = "IndexError: list index out of range while accessing array element 5"
    bug_report = IssueParser.parse(raw_text)
    assert bug_report.title.startswith("IndexError")
    assert "IndexError: list index out of range" in bug_report.actual_behavior

