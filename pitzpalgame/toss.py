import random

# from abc import ABC, abstractmethod


def action(data):
    if "Players" not in data and "Status" not in data and "Board" not in data:
        return False
    players = data["Players"]
    shuffled = random.sample(players, len(players))
    ret = []
    side = 0
    for player in shuffled:
        ret.append({player: side})
        side += 1
    data["Toss"] = ret
    data["Status"] = "active"
    data["Board"]["Turn"] = 0
    data["Moves"] = []
    return True
