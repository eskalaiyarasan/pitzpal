import ast
import json

import move

# from django.test import TestCase
import newgame as ng
import toss
import utils

# Create your tests here.

xnew = {
    "Name": {"Value": "classic_one_pod"},
    "Level": {"Value": "easy"},
    "Players": ["testone", "newone"],
}
x = ng.newgame.from_json(xnew)
y = x.build()
toss.action(y)
with open("output_game.json", "w") as f:
    json.dump(y, f)

inp = input("choose>pit#")
req = {
    "GameID": y["GameID"],
    "Move": {
        "Sequence": 1,
        "Timestamp": utils.get_timestamp_str(),
        "Player": y["Toss"][0]["Player"],
        "Index": int(inp),
    },
}
content = ""
with open("output_game.json", "r") as file:
    content = file.read()

game_data = json.loads(content)
# data_dict = ast.literal_eval(str(req))
# reqdata = json.dumps(data_dict)
outdata = move.move(game_data, req)
with open("output_game.json", "w") as f:
    f.write(outdata)
