import copy
import random

from . import game, movereq, utils


def move(game_in, data, detail=[]):
    ret = {}
    x = game.game.from_json(game_in)
    req = movereq.movereq.from_json(data)
    # print("move:", data)
    try:
        ret = x.move(req, detail)
    except Exception as e:
        print(f"exception : move{data} : {e}")
    print("move:", ret)
    return str(ret)


def createreq(y):
    ret = {"GameID": y["GameID"], "Move": {}}
    seq = 1
    turn = y["Board"]["Turn"]
    if ("Moves" in y) and (len(y["Moves"]) > 0):
        seq = y["Moves"][-1]["Move"]["Sequence"]
    ret["Move"]["Sequence"] = seq + 1
    ret["Move"]["Timestamp"] = utils.get_timestamp_str()
    ret["Move"]["Player"] = y["Toss"][turn]["Player"]
    choice = True
    npits = y["Config"]["PitsPerSide"]
    pits = range(npits * turn, npits * (turn + 1))
    while choice:
        inp = random.choice(pits)
        print("createreq", inp)
        x = y["Board"]["Pits"][inp]
        if (x["Active"] is True) and (x["Value"] > 0) and (x["Public"] is False):
            ret["Move"]["Index"] = inp
            choice = False
            print("createreq", inp, "------- done")
    return ret


def resign(yy, player):
    y = copy.deepcopy(yy)
    who = -1
    for side in y["Toss"]:
        if player.strip() == side["Player"].strip():
            who = side["Side"]
            break
    if who != -1:
        for pit in y["Board"]["Pits"]:
            if y["Config"]["Kingzpits"]:
                if pit["Index"] in y["Config"]["Kingzpits"]["Value"]:
                    continue
            if pit["Side"] == who:
                pit["Active"] = False

        y["Board"]["Store"][who][str(who)] = 0
        nps = 0
        npi = {}
        for person in y["Toss"]:
            if person["Side"] == who:
                person["Active"] = False
            if person["Active"]:
                nps += 1
                npi = person
        if nps == 1:
            y["Status"] = "done"
            y["Report"] = {
                "EndType": "resignation",
                "Winner": {"Player": npi["Player"], "Side": npi["Side"]},
            }
            print("resign: gameover: winner", npi)
    return y


def updateReport(y, out, player):
    is_win = False
    if out["Status"] == "done" and y["Status"] == "active":
        print(y)
        store = out["Board"]["Store"]
        store.sort(key=lambda obj: list(obj.values())[0], reverse=True)
        win_side = int(list(store[0].items())[0][0])
        result = next(
            (item["Player"] for item in y["Toss"] if item["Side"] == win_side), None
        )
        if (result is not None) and (result == player):
            is_win = True
        out["Report"] = {
            "EndType": "graceful",
            "Winner": {"Player": result, "Side": win_side},
        }
    return is_win
