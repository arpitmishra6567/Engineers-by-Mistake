"""
Unit tests for calculate_average function.
Demonstrates the failing behavior on empty lists prior to repair.
"""

import pytest
from average import calculate_average


def test_normal_list():
    """Normal list returns its arithmetic mean."""
    assert calculate_average([2, 4, 6]) == 4.0
    assert calculate_average([10, 20]) == 15.0


def test_single_element_list():
    """Single element list returns that element value."""
    assert calculate_average([42]) == 42.0


def test_empty_list_raises_value_error():
    """Empty list must raise ValueError, not unhandled ZeroDivisionError."""
    with pytest.raises(ValueError, match="Cannot calculate average of an empty list"):
        calculate_average([])

