# from . import pit, utils
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
        instance = cls()
        if validate_schema:
            instance.validate_schema(data)

        # 2. Update _storage with a deep copy of the input JSON
        pits_list = []
        for pitx in data["Pits"]:
            pitz = pit.pit.from_json(pitx)
            pits_list.append(pitz)

        instance._storage["Pits"] = pits_list
        instance._storage["Turn"] = data["Turn"]

        return instance


def createBoard(data: dict):
    ret = {}
    pits = []
    if "PitsPerSide" in data and "Nside" in data and "Nseeds" in data:
        for i in range(data["Nside"]):
            for j in range(data["PitsPerSide"]):
                z = (i * data["PitsPerSide"]) + j
                xnew = {
                    "Index": z,
                    "Active": True,
                    "Value": data["Nseeds"],
                    "Side": i,
                }
                if (
                    "Kingzpits" in data
                    and "Enable" in data["Kingzpits"]
                    and data["Kingzpits"]["Enable"]
                ):
                    value = data["Kingzpits"]["Value"]
                    share = []
                    if z in value:
                        for k in range(data["Nside"]):
                            share.append({str(k): 0})
                    xnew["Share"] = share

                pits.append(xnew)
        ret = {"Pits": pits, "Turn": 0}
    return ret
