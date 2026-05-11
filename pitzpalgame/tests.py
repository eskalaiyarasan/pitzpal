import json

# from django.test import TestCase
import newgame as ng
import toss

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
