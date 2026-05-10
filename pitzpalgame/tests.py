import json

# from django.test import TestCase
import newgame as ng

# Create your tests here.

xnew = {
    "Name": {"Value": "classic_one_pod"},
    "Level": {"Value": "easy"},
    "Players": ["testone", "newone"],
}
x = ng.newgame.from_json(xnew)
# y = x.build()
with open("output_game.json", "w") as f:
    f.write(str(x))
