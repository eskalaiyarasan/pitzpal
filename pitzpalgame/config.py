import copy
import json

# from . import utils
from . import utils


class CoreGameConfig(utils.Base):
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__init__(
            "config.schema.json",
            "Config",
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

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "CoreGameConfig":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)

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
        result, ret = _create(
            algo, diffx, ret, "pitzpalgame/rules/json/classic.json", "classic"
        )
        result, ret = _create(
            algo, diffx, ret, "pitzpalgame/rules/json/one.json", "one"
        )
        result, ret = _create(
            algo + "_pro", diffx, ret, "pitzpalgame/rules/json/pro.json", "pro"
        )
        result, ret = _create(
            algo, diffx, ret, "pitzpalgame/rules/json/kingz.json", "kingz"
        )
    return ret
