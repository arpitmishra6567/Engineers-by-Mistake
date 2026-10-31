"""
Calculation module with an intentional zero-division defect on empty input.
"""


def calculate_average(numbers):
    """
    Calculate the arithmetic mean of a list of numbers.
    Should raise ValueError if the numbers sequence is empty.
    """
    return sum(numbers) / len(numbers)

