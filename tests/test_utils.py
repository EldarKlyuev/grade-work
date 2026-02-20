"""Test utility functions"""

from src.app.infrastructure.utils.base64_utils import decode_base64, encode_base64
from src.app.infrastructure.utils.json_yaml_converter import json_to_yaml
from src.app.infrastructure.utils.string_utils import (
    concatenate_strings,
    filter_strings_starting_with_a,
    get_string_lengths,
)


def test_base64_encode_decode():
    """Test base64 encoding and decoding"""
    original = "Hello, World!"
    encoded = encode_base64(original)
    decoded = decode_base64(encoded)
    assert decoded == original


def test_json_to_yaml():
    """Test JSON to YAML conversion"""
    json_data = '{"name": "John", "age": 30}'
    yaml_result = json_to_yaml(json_data)
    assert "name: John" in yaml_result
    assert "age: 30" in yaml_result


def test_get_string_lengths():
    """Test map function for string lengths"""
    strings = ["hello", "world", "python"]
    lengths = get_string_lengths(strings)
    assert lengths == [5, 5, 6]


def test_filter_strings_starting_with_a():
    """Test filter function for strings starting with A"""
    strings = ["Apple", "Banana", "Avocado", "Cherry", "apricot"]
    filtered = filter_strings_starting_with_a(strings)
    assert filtered == ["Apple", "Avocado", "apricot"]


def test_concatenate_strings():
    """Test reduce function for string concatenation"""
    strings = ["hello", "world", "python"]
    result = concatenate_strings(strings, " ")
    assert result == "hello world python"
    
    result = concatenate_strings(strings, "-")
    assert result == "hello-world-python"
