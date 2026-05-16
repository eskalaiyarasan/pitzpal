import ast
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import move, toss
from . import newgame as ng
from .models import PitzpalGame


def start_game(request):
    if request.method == "POST":
        data = json.loads(request.body)
        data["Players"] = [
            str(request.user.username),
            "Computer-1ae4de1c-4ac5-3e42ec2d59e0",
        ]
        x = ng.newgame.from_json(data)
        y = x.build()
        new_game = PitzpalGame.objects.create(player1=request.user, game=y)
        # Return only the GameID as requested
        return JsonResponse(
            {"GameID": str(new_game.id), "Board": y["Board"], "Status": y["Status"]}
        )


def toss_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=data["GameID"])
        y = z.game
        toss.action(y)
        z.game = y
        z.save()
        return JsonResponse(
            {
                "GameID": data["GameID"],
                "Board": y["Board"],
                "Toss": y["Toss"],
                "Status": y["Status"],
                "Error": {"Value": 0},
            }
        )


def make_comp_move(request):
    if request.method == "POST":
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=data["GameID"])
        y = z.game
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == "Computer-1ae4de1c-4ac5-3e42ec2d59e0":
                req = move.createreq(y)
                outdata = move.move(y, req)
                y = ast.literal_eval(outdata)
        except Exception as e:
            print(f"exception {e}")
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
            return JsonResponse(
                {
                    "GameID": data["GameID"],
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 0},
                    "Moves": y["Moves"],
                }
            )
        else:
            y = z.game
            return JsonResponse(
                {
                    "GameID": data["GameID"],
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 14},
                    "Moves": y["Moves"],
                }
            )


def make_move(request):
    if request.method == "POST":
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=data["GameID"])
        y = z.game
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == str(request.user.username):
                req = data
                outdata = move.move(y, req)
                y = ast.literal_eval(outdata)
        except Exception as e:
            print(f"exception {e}")
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
            return JsonResponse(
                {
                    "GameID": data["GameID"],
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 0},
                    "Moves": y["Moves"],
                }
            )
        else:
            y = z.game
            return JsonResponse(
                {
                    "GameID": data["GameID"],
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 14},
                    "Moves": y["Moves"],
                }
            )


def refresh(request):
    if request.method in ["POST", "GET"]:
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=data["GameID"])
        y = z.game
        ret = {
            "GameID": data["GameID"],
            "Board": y["Board"],
            "Toss": y["Toss"],
            "Error": {"Value": 0},
        }
        if y["Status"] != "toss":
            ret["Status"] = (y["Status"],)
        return JsonResponse(ret)
