import random

from . import game, movereq, utils


def move(game_in, data):
    ret = {}
    x = game.game.from_json(game_in)
    req = movereq.movereq.from_json(data)
    print("move:", data)
    try:
        ret = x.move(req)
    except Exception as e:
        print(f"exception : move{data} : {e}")
    return str(ret)


def createreq(y):
    ret = {"GameID": y["GameID"], "Move": {}}
    seq = 1
    turn = y["Board"]["Turn"]
    if ("Moves" in y) and (len(y["Moves"]) > 0):
        seq = y["Moves"][-1]["Sequence"]
    ret["Move"]["Sequence"] = seq + 1
    ret["Move"]["Timestamp"] = utils.get_timestamp_str()
    ret["Move"]["Player"] = y["Toss"][turn]["Player"]
    choice = True
    npits = y["Config"]["PitsPerSide"]
    pits = range(npits * turn, npits * (turn + 1))
    while choice:
        inp = random.choice(pits)
        if (y["Board"]["Pits"][inp]["Active"]) and (
            y["Board"]["Pits"][inp]["Value"] > 0
        ):
            ret["Move"]["Index"] = inp
            choice = False
    return ret
