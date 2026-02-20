"""Utility endpoints router"""

from fastapi import APIRouter, HTTPException, status

from src.app.infrastructure.utils.base64_utils import decode_base64, encode_base64
from src.app.infrastructure.utils.json_yaml_converter import json_to_yaml
from src.app.infrastructure.utils.string_utils import (
    concatenate_strings,
    filter_strings_starting_with_a,
    get_string_lengths,
)
from src.app.presentation.schemas import (
    Base64DecodeRequest,
    Base64EncodeRequest,
    JsonToYamlRequest,
)

router = APIRouter(prefix="/utils", tags=["Utils"])


@router.post("/json-to-yaml")
async def convert_json_to_yaml(request: JsonToYamlRequest) -> dict[str, str]:
    """Convert JSON to YAML format"""
    try:
        yaml_content = json_to_yaml(request.json_data)
        return {"yaml": yaml_content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}",
        )


@router.post("/base64/encode")
async def encode_to_base64(request: Base64EncodeRequest) -> dict[str, str]:
    """Encode string to Base64"""
    encoded = encode_base64(request.data)
    return {"encoded": encoded}


@router.post("/base64/decode")
async def decode_from_base64(request: Base64DecodeRequest) -> dict[str, str]:
    """Decode Base64 string"""
    try:
        decoded = decode_base64(request.encoded_data)
        return {"decoded": decoded}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Base64: {str(e)}",
        )


@router.post("/strings/lengths")
async def string_lengths(strings: list[str]) -> dict[str, list[int]]:
    """Get string lengths using map"""
    lengths = get_string_lengths(strings)
    return {"lengths": lengths}


@router.post("/strings/filter-a")
async def filter_a_strings(strings: list[str]) -> dict[str, list[str]]:
    """Filter strings starting with 'A' using filter"""
    filtered = filter_strings_starting_with_a(strings)
    return {"filtered": filtered}


@router.post("/strings/concatenate")
async def concat_strings(strings: list[str], separator: str = " ") -> dict[str, str]:
    """Concatenate strings using reduce"""
    result = concatenate_strings(strings, separator)
    return {"result": result}
