# from . import pit, utils
import copy

import pit
import utils


class Board(utils.Base):
    def __init__(self) -> None:
        # Pass the specific starting data to the base constructor
        super().__init__("board.schema.json", "Board", {"Pits": [], "Turn": 0})

    @classmethod
    def from_json(cls, data: dict, validate_schema: bool = True) -> "board":
        """Validates and creates instance, then updates storage with input JSON."""
        # 1. Create instance with random values initially
        if isinstance(data, str):
            data = json.loads(data)
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)

        # 2. Update _storage with a deep copy of the input JSON
        pits_list = []
        for pitx in data["Pits"]:
            pitz = pit.pit.from_json(pitx)
            pits_list.append(pitz)
        params = ["Turn", "Store", "TotalSeeds"]
        instance._storage["Pits"] = pits_list
        for param in params:
            instance._storage[param] = copy.deepcopy(data[param])
        return instance


def createBoard(data: dict):
    ret = {}
    pits = []
    total = 0
    store = []
    if "PitsPerSide" in data and "Nside" in data and "Nseeds" in data:
        for i in range(data["Nside"]):
            store.append({str(i): 0})
            for j in range(data["PitsPerSide"]):
                z = (i * data["PitsPerSide"]) + j
                xnew = {
                    "Index": z,
                    "Active": True,
                    "Side": i,
                }
                if (
                    "Kingzpits" in data
                    and "Enable" in data["Kingzpits"]
                    and data["Kingzpits"]["Enable"]
                ):
                    value = data["Kingzpits"]["Value"]
                    share = []
                    xnew["Value"] = 0  #: data["Nseeds"],
                    if z in value:
                        for k in range(data["Nside"]):
                            share.append({str(k): 0})
                    xnew["Share"] = share
                else:
                    xnew["Value"] = data["Nseeds"]
                    total += data["Nseeds"]

                pits.append(xnew)
        ret = {"Pits": pits, "Turn": 0, "TotalSeeds": total, "Store": store}
    return ret
