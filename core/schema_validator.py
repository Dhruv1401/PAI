# core/schema_validator.py
import jsonschema
import json

startup_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
            "content": {"type": "string"},
            "timestamp": {"type": "string"}
        },
        "required": ["role", "content", "timestamp"]
    }
}

def validate_memory_schema(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=startup_schema)
        return True
    except Exception as e:
        print(f"[SchemaValidator] Error: {e}")
        return False
