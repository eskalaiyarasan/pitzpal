import copy
import json

import utils


class errorExp(Exception):
    pass


def create_error_class(error_name, value):
    # type() creates a new class:
    # 1. Name of the class
    # 2. Bases (inheriting from Exception)
    # 3. Dict of attributes (we'll add a 'code' attribute for fun)
    return type(error_name, (errorExp,), {"code": value})


class error(utils.Base):
    def __init__(self):
        with open("rules/json/error.json") as sf:
            data = json.load(sf)
        self._exp = {
            k: create_error_class(k, v)
            for item in data["SubType"]
            for k, v in item.items()
        }
        super().__init__("error.schema.json", "Error", data)

    def raiseExp(self, k):
        if k in self._exp:
            raise self._exp[k]()

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "error":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)
        instance._storage = copy.deepcopy(data)
        return instance
