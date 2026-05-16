import copy
import uuid

# from . import board, config, game
from . import board, config, utils


class newgame(utils.Base):
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__init__("gamenew.schema.json", "NewGame", {})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "newgame":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()

        if validate_schema:
            instance.validate_schema(data)

        # 2. Update _storage with a deep copy of the input JSON
        instance._storage = copy.deepcopy(data)

        return instance

    def build(self):
        xnew = {
            "GameID": str(uuid.uuid4()),
            "Name": self._storage["Name"],
            "Level": self._storage["Level"],
            "Players": self._storage["Players"],
            "CreatedAt": utils.get_timestamp_str(),
            "Config": config.createConfig(
                self._storage["Name"], self._storage["Level"]
            ),
        }
        # check number of players == number of sides
        # if len(xnew["Players"]) != xnew["Config"]["Nside"]:
        # return None

        xnew["Board"] = board.createBoard(xnew["Config"])
        xnew["Status"] = "toss"
        return xnew
