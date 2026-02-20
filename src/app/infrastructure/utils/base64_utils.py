"""Base64 encoding and decoding utilities"""

import base64


def encode_base64(data: str) -> str:
    """
    Encode string to Base64
    
    Args:
        data: String to encode
        
    Returns:
        Base64 encoded string
    """
    data_bytes = data.encode('utf-8')
    encoded_bytes = base64.b64encode(data_bytes)
    return encoded_bytes.decode('utf-8')


def decode_base64(encoded_data: str) -> str:
    """
    Decode Base64 string
    
    Args:
        encoded_data: Base64 encoded string
        
    Returns:
        Decoded string
    """
    encoded_bytes = encoded_data.encode('utf-8')
    decoded_bytes = base64.b64decode(encoded_bytes)
    return decoded_bytes.decode('utf-8')


def encode_base64_bytes(data: bytes) -> str:
    """
    Encode bytes to Base64
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base64 encoded string
    """
    encoded_bytes = base64.b64encode(data)
    return encoded_bytes.decode('utf-8')


def decode_base64_bytes(encoded_data: str) -> bytes:
    """
    Decode Base64 string to bytes
    
    Args:
        encoded_data: Base64 encoded string
        
    Returns:
        Decoded bytes
    """
    encoded_bytes = encoded_data.encode('utf-8')
    return base64.b64decode(encoded_bytes)
