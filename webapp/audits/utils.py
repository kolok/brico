"""Utility functions for the audits app."""

from natsort import natsort_keygen

# Create a natural sort key generator that handles decimals and alphanumeric strings
_natural_sort_key = natsort_keygen()


def natural_sort_key(value: str) -> tuple:
    """
    Generate a sort key for natural sorting using natsort.

    Handles decimal numbers numerically and other strings alphanumerically.
    Examples:
        - "1.1" -> sorts before "10.1" (numeric)
        - "4.2" -> sorts before "4.11" (numeric, correct decimal ordering)
        - "CRI-001" -> sorts alphanumerically

    Args:
        value: The string value to generate a sort key for.

    Returns:
        A tuple that can be used for sorting with natural ordering.
    """
    if not value:
        return _natural_sort_key("")
    return _natural_sort_key(value)
