"""JSON to YAML converter"""

import json

import yaml


def json_to_yaml(json_data: str | dict) -> str:
    """
    Convert JSON to YAML format
    
    Args:
        json_data: JSON string or dictionary
        
    Returns:
        YAML formatted string
    """
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def yaml_to_json(yaml_data: str) -> str:
    """
    Convert YAML to JSON format
    
    Args:
        yaml_data: YAML string
        
    Returns:
        JSON formatted string
    """
    data = yaml.safe_load(yaml_data)
    return json.dumps(data, indent=2)
