import copy
import uuid

# from . import board, config, game
import board
import config
import jsonschema
import utils


class newgame:
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__setattr__(
            "_storage",
            {"Pits": []},
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
    def from_json(cls, data: dict, validate_schema: bool = True) -> "newgame":
        """Validates and creates instance, then updates storage with input JSON."""
        if validate_schema:
            root, store = utils.prepare_schemas("gamenew.schema.json", "NewGame")
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

    def build(self):
        xnew = {
            "GameID": str(uuid.uuid4()),
            "Name": self._storage["Name"],
            "Level": self._storage["Level"],
            "Players": self._storage["Players"],
            "Config": config.createConfig(
                self._storage["Name"], self._storage["Level"]
            ),
        }
        # check number of players == number of sides
        if len(xnew["Players"]) != xnew["Config"]["Nside"]:
            return None

        xnew["Board"] = board.createBoard(xnew["Config"])
        xnew["Status"] = "toss"
        return xnew
