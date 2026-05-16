import copy

from . import utils


class movereq(utils.Base):
    def __init__(self):
        super().__init__("movereq.schema.json", "MoveReq", {})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "movereq":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)
        # 2. Update _storage with a deep copy of the input JSON
        instance._storage = copy.deepcopy(data)
        return instance
