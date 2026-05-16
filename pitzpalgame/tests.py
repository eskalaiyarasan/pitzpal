import ast
import json
import random

import move

# from django.test import TestCase
import newgame as ng
import toss
import utils


# Create your tests here.
def print_board(y1):
    print("=======================================")
    print("    store:", y1["Store"])
    print("= = = = = = = = = = = = = = = = = = = =")
    for pit in y1["Pits"]:
        active = "✓" if pit["Active"] else "✗"
        print("\t", active, pit["Index"], pit["Value"])
    print("=======================================")


xnew = {
    "Name": {"Value": "classic_one_pod"},
    "Level": {"Value": "easy"},
    "Players": ["testone", "newone"],
}
x = ng.newgame.from_json(xnew)
y = x.build()
toss.action(y)
filename = "output/new_game.json"
with open(filename, "w") as f:
    json.dump(y, f)
inp = 0
sequence = 0
try:
    while y["Status"] != "done":
        turn = y["Board"]["Turn"]
        sequence += 1
        pits = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
        print_board(y["Board"])
        if turn == 1:
            inp = input("input:")
        else:
            choice = True
            while choice:
                inp = random.choice(pits[turn])
                if (y["Board"]["Pits"][inp]["Active"]) and (
                    y["Board"]["Pits"][inp]["Value"] > 0
                ):
                    choice = False

        req = {
            "GameID": y["GameID"],
            "Move": {
                "Sequence": sequence,
                "Timestamp": utils.get_timestamp_str(),
                "Player": y["Toss"][turn]["Player"],
                "Index": int(inp),
            },
        }
        content = ""
        with open(filename, "r") as file:
            content = file.read()

        game_data = json.loads(content)
        outdata = move.move(game_data, req)
        y = ast.literal_eval(outdata)
        # reqdata = json.dumps(data_dict)
        filename = "output/move_" + str(sequence) + ".json"
        with open(filename, "w") as f:
            json.dump(y, f)
except Exception as e:
    print(f"exception {e}")
