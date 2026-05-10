import copy
import json
import os
from collections.abc import Mapping

import jsonschema

# directory = "pitzpalgame/rules/schema"
directory = "rules/schema"
store = {}
_once = True


def prepare_schemas(root_json, root_param):
    """Loads all schemas and prepares them for cross-referenced validation."""
    global store, _once
    root = None

    if _once:
        _once = False
        for filename in os.listdir(directory):
            filename = os.path.join(directory, filename)
            if filename.endswith(".json"):
                schema_data = None
                print(f"file: {filename}")
                with open(filename) as sf:
                    schema_data = json.load(sf)
                store[schema_data["$id"]] = schema_data

    for id in store:
        if root_json.strip() in id:
            schema = store[id]
            root = copy.deepcopy(schema)
            root.update(schema["$defs"][root_param.strip()])
    return root, store


def deep_merge(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            deep_merge(dict1[key], value)
        else:
            dict1[key] = value
    return dict1
