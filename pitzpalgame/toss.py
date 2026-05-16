import copy
import random

from . import utils

# from abc import ABC, abstractmethod


def action(data):
    if "Players" not in data and "Status" not in data and "Board" not in data:
        return False
    players = data["Players"]
    shuffled = random.sample(players, len(players))
    ret = []
    side = 0
    for player in shuffled:
        ret.append({"Player": player, "Side": side})
        side += 1
    data["Toss"] = ret
    data["Status"] = "active"
    data["Board"]["Turn"] = 0
    data["Moves"] = []
    return True


class toss(utils.Base):
    def __init__(self):
        super().__init__("toss.schema.json", "Toss", {})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "toss":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)
        # 2. Update _storage with a deep copy of the input JSON
        instance._storage = copy.deepcopy(data)
