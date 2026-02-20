"""String manipulation utilities using map, filter, and reduce"""

from functools import reduce


def get_string_lengths(strings: list[str]) -> list[int]:
    """
    Get lengths of each string using map
    
    Args:
        strings: List of strings
        
    Returns:
        List of string lengths
        
    Example:
        >>> get_string_lengths(["hello", "world", "python"])
        [5, 5, 6]
    """
    return list(map(len, strings))


def filter_strings_starting_with_a(strings: list[str]) -> list[str]:
    """
    Filter strings that start with 'A' (case-insensitive) using filter
    
    Args:
        strings: List of strings
        
    Returns:
        List of strings starting with 'A'
        
    Example:
        >>> filter_strings_starting_with_a(["Apple", "Banana", "Avocado", "Cherry"])
        ['Apple', 'Avocado']
    """
    return list(filter(lambda s: s.lower().startswith('a'), strings))


def concatenate_strings(strings: list[str], separator: str = " ") -> str:
    """
    Concatenate strings using reduce
    
    Args:
        strings: List of strings
        separator: Separator between strings
        
    Returns:
        Concatenated string
        
    Example:
        >>> concatenate_strings(["hello", "world", "python"], " ")
        'hello world python'
    """
    if not strings:
        return ""
    
    return reduce(lambda a, b: f"{a}{separator}{b}", strings)


def sum_string_lengths(strings: list[str]) -> int:
    """
    Sum all string lengths using reduce
    
    Args:
        strings: List of strings
        
    Returns:
        Total length of all strings
        
    Example:
        >>> sum_string_lengths(["hello", "world"])
        10
    """
    return reduce(lambda total, s: total + len(s), strings, 0)


def filter_and_map_strings(
    strings: list[str],
    min_length: int = 3,
) -> list[str]:
    """
    Filter strings by minimum length and convert to uppercase
    Demonstrates chaining filter and map
    
    Args:
        strings: List of strings
        min_length: Minimum string length
        
    Returns:
        Filtered and uppercased strings
        
    Example:
        >>> filter_and_map_strings(["a", "hello", "hi", "python"], 3)
        ['HELLO', 'PYTHON']
    """
    filtered = filter(lambda s: len(s) >= min_length, strings)
    return list(map(str.upper, filtered))
