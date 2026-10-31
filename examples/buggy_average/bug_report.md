# ZeroDivisionError in calculate_average on empty list

## Expected Behavior
When an empty list `[]` is passed to `calculate_average(numbers)`, the function should raise an explicit `ValueError("Cannot calculate average of an empty list")`.

## Actual Behavior
The function raises an unhandled `ZeroDivisionError: division by zero` because `len(numbers)` is 0.

## Error Message & Stack Trace
```text
ZeroDivisionError: division by zero
  File "average.py", line 10, in calculate_average
    return sum(numbers) / len(numbers)
```

## Reproduction Command
```bash
python -m pytest test_average.py
```

