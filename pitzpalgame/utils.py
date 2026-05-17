import copy
import json
import os
from abc import abstractmethod
from datetime import datetime, timedelta, timezone

import jsonschema

directory = "pitzpalgame/rules/schema"
# directory = "rules/schema"
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


def get_timestamp_str():
    # 1. Generate current time in UTC (Recommended for Logs/Trace)
    now_utc = datetime.now(timezone.utc)
    # 2. To get the specific "Z" suffix (shorthand for Zulu/UTC)
    z_timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    return str(z_timestamp)


class Base:
    def __init__(self, schema="", myname="", initial_data=None) -> None:
        # Use super() to avoid triggering our custom __setattr__ immediately
        self.schema = schema
        self.myname = myname
        super().__setattr__("_storage", initial_data or {})

    def __getattr__(self, ppty):
        # This is only called if ppty isn't in __dict__
        if ppty in self._storage:
            return self._storage[ppty]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{ppty}'"
        )

    def __setattr__(self, ppty, value):
        # If it's already in storage, keep it there
        if "_storage" in self.__dict__ and ppty in self._storage:
            self._storage[ppty] = value
        else:
            # Otherwise, set it normally on the object
            super().__setattr__(ppty, value)

    def __str__(self):
        return str(self._storage)

    def __repr__(self):
        return str(self._storage)

    def validate_schema(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        root, store = prepare_schemas(self.schema, self.myname)
        resolver = jsonschema.RefResolver.from_schema(root, store=store)
        try:
            jsonschema.validate(instance=data, schema=root, resolver=resolver)
            # print("✓ Validation Successful")
            return True
        except Exception as e:
            print(f"✗ Validation Failed: {e}")
            raise
        return False

    def __deepcopy__(self, memo):
        # 1. Create a new instance of the same class (e.g., movereq)
        # We bypass the standard __init__ if we don't want to re-run validation
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # 2. Copy the simple attributes normally
        result.schema = self.schema
        result.myname = self.myname

        # 3. Deep copy the _storage dictionary specifically
        result._storage = copy.deepcopy(self._storage, memo)

        return result

    # @abstractmethod
    # def to_json(self):
    #     pass
