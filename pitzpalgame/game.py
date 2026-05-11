import copy

import jsonschema
import utils


class game(utils.Base):
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__init__("game.schema.json", "Game", {})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "game":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)
        # 2. Update _storage with a deep copy of the input JSON
        instance._storage = copy.deepcopy(data)

        return instance
