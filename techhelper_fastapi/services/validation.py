"""Validation helpers for form field parsing and validation.

This module provides reusable functions for validating and parsing form input,
reducing code duplication across tool CRUD endpoints.
"""

from typing import Optional


def parse_optional_float(
    value: str,
    field_name: str,
    errors: list[str],
    allow_negative: bool = False,
) -> Optional[float]:
    """Parse an optional string field to float, adding errors if invalid.
    
    Args:
        value: The string value from form input (may be empty or whitespace)
        field_name: Human-readable field name for error messages
        errors: List to append error messages to
        allow_negative: If False, negative values will be rejected
        
    Returns:
        Parsed float value, or None if the field was empty/whitespace
        
    Example:
        >>> errors = []
        >>> val = parse_optional_float("10.5", "Posuw", errors)
        >>> val
        10.5
        >>> errors
        []
        
        >>> val = parse_optional_float("invalid", "Posuw", errors)
        >>> val is None
        True
        >>> errors
        ['Posuw musi być liczbą']
    """
    stripped = value.strip() if value else ""
    if not stripped:
        return None
    
    try:
        result = float(stripped)
        if not allow_negative and result < 0:
            errors.append(f"{field_name} nie może być ujemna/ujemny")
        return result
    except ValueError:
        errors.append(f"{field_name} musi być liczbą")
        return None


def parse_optional_int(
    value: str,
    field_name: str,
    errors: list[str],
    allow_negative: bool = False,
) -> Optional[int]:
    """Parse an optional string field to int, adding errors if invalid.
    
    Args:
        value: The string value from form input (may be empty or whitespace)
        field_name: Human-readable field name for error messages
        errors: List to append error messages to
        allow_negative: If False, negative values will be rejected
        
    Returns:
        Parsed int value, or None if the field was empty/whitespace
    """
    stripped = value.strip() if value else ""
    if not stripped:
        return None
    
    try:
        result = int(stripped)
        if not allow_negative and result < 0:
            errors.append(f"{field_name} nie może być ujemna/ujemny")
        return result
    except ValueError:
        errors.append(f"{field_name} musi być liczbą całkowitą")
        return None
