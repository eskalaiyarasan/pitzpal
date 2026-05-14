import copy

import algo.algo as algo
import board
import config
import error
import movereq
import utils


class game(utils.Base):
    def __init__(self) -> None:
        # Initialize with random/default values provided to constructor
        super().__init__("game.schema.json", "Game", {"GameID": 0})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "game":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        params = ["Name", "Level", "Players", "CreatedAt", "Status", "Moves", "Toss"]
        if validate_schema:
            instance.validate_schema(data)
        # 2. Update _storage with a deep copy of the input JSON
        instance._storage["GameID"] = copy.deepcopy(data["GameID"])
        for param in params:
            if param in data:
                instance._storage[param] = copy.deepcopy(data[param])

        if "Config" in data:
            instance._storage["Config"] = config.CoreGameConfig.from_json(
                data["Config"]
            )
        if "Board" in data:
            instance._storage["Board"] = board.Board.from_json(data["Board"])
        return instance

    def move(self, data: movereq.movereq):
        # if self.GameID != data.GameID:
        #     error.error().raiseExp("GameMismatch")
        return algo.move(self, data)
