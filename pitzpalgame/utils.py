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


def deep_merge(A: dict, B: dict) -> dict:
    """
    Deep-merge dicts A and B into a new dict.
    [    - Recursively merges nested dicts.
    - When keys conflict, A's value takes precedence over B's.
    - Does not mutate A or B.
    """

    def _merge(a, b):
        # Start from a deep copy of b so we don't mutate inputs
        result = copy.deepcopy(b)
        for k, a_val in a.items():
            if k in result:
                b_val = result[k]
                if isinstance(a_val, Mapping) and isinstance(b_val, Mapping):
                    result[k] = _merge(a_val, b_val)  # merge nested dicts
                else:
                    result[k] = copy.deepcopy(a_val)  # A overrides B
            else:
                result[k] = copy.deepcopy(a_val)  # add new key from A
        return result

    return _merge(A, B)
