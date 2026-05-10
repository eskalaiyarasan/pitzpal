import copy
import json

import jsonschema

# from . import utils
import utils


class CoreGameConfig:
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__setattr__(
            "_storage",
            {
                "PitsPerSide": 0,
                "Nside": 0,
                "Nseeds": 0,
                "Algorithm": {"Value": "classic"},
                "Early": {"Enable": False},
                "Kingzpits": {"Enable": False},
                "Plus": {"Enable": False},
                "Relay": {"Enable": False},
            },
        )

    def __getattr__(self, ppty):
        if "_storage" in self.__dict__ and ppty in self._storage:
            return self._storage[ppty]
        raise AttributeError(f"Key '{ppty}' not found")

    def __setattr__(self, ppty, value):
        if ppty == "_storage":
            super().__setattr__(ppty, value)
        elif "_storage" in self.__dict__ and ppty in self._storage:
            self._storage[ppty] = value
        else:
            super().__setattr__(ppty, value)

    def __str__(self):
        return str(self._storage)

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "CoreGameConfig":
        """Validates and creates instance, then updates storage with input JSON."""
        if validate_schema:
            root, store = utils.prepare_schemas("config.schema.json", "Config")
            resolver = jsonschema.RefResolver.from_schema(root, store=store)
            try:
                jsonschema.validate(instance=data, schema=root, resolver=resolver)
                print("✓ Validation Successful")
            except Exception as e:
                print(f"✗ Validation Failed: {e}")
                raise

        # 1. Create instance with random values initially
        instance = cls()

        # 2. Update _storage with a deep copy of the input JSON
        instance._storage = copy.deepcopy(data)

        return instance


def _create(algo, diffx, ret, json_file, name):
    # print(f"{algo}, {diffx}, ret, {json_file}, {name}")
    if name in algo.strip().split("_"):
        with open(json_file) as sf:
            content = json.load(sf)
        if diffx in content:
            data = content[diffx]
        else:
            return [False, ret]
        ret1 = utils.deep_merge(ret, data)
        # print(f"_create {ret}, json_file, {name}")
        return [True, ret1]
    return [False, ret]


def createConfig(name: dict, level: dict):
    ret = {}
    print(f"{name}, {level}")
    if "Value" in name and "Value" in level:
        algo = name["Value"]
        diffx = level["Value"]
        result, ret = _create(algo, diffx, ret, "rules/json/classic.json", "classic")
        result, ret = _create(algo, diffx, ret, "rules/json/one.json", "one")
        result, ret = _create(algo, diffx, ret, "rules/json/pod.json", "pod")
    return ret
