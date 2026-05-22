import ast
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from pitzpalgame import move, toss
from pitzpalgame import newgame as ng

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


def toss_action(request, game_id):
    if request.method in ["POST", "GET"]:
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": game_id,
            "Board": y["Board"],
            "Status": y["Status"],
            "Error": {"Value": 0},
        }
        if y["Status"] == "toss":
            toss.action(y)
            z.game = y
            z.save()
            ret["Toss"] = y["Toss"]
        else:
            ret["Toss"] = y["Toss"]
            ret["Error"] = {"Value": 17}
        return JsonResponse(ret)


def update_stat_at_end(request, y, out):
    if out["Status"] == "done" and y["Status"] == "active":
        print(y)
        store = out["Board"]["Store"]
        store.sort(key=lambda obj: list(obj.values())[0], reverse=True)
        win_side = int(list(store[0].items())[0][0])
        result = next(
            (item["Player"] for item in y["Toss"] if item["Side"] == win_side), None
        )
        is_win = False
        if (result is not None) and (result == str(request.user.username)):
            is_win = True
        request.user.complete_game(is_win=is_win, difficulty=y["Level"]["Value"])


def make_comp_move(request, game_id):
    if request.method == "POST":
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == "Computer-1ae4de1c-4ac5-3e42ec2d59e0":
                req = move.createreq(y)
                outdata = move.move(y, req)
                out = ast.literal_eval(outdata)
                try:
                    update_stat_at_end(request, y, out)
                except Exception as e:
                    print(f"update_stat_at_end {e}")
                y = out
        except Exception as e:
            print(f"exception {e}")
            y = {}
        if len(y) > 0:
            z.game = y
            z.save()
            return JsonResponse(
                {
                    "GameID": game_id,
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
                    "GameID": game_id,
                    "Board": y["Board"],
                    "Toss": y["Toss"],
                    "Status": y["Status"],
                    "Error": {"Value": 14},
                    "Moves": y["Moves"],
                }
            )


def make_move(request, game_id):
    if request.method == "POST":
        data = json.loads(request.body)
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        try:
            turn = y["Board"]["Turn"]
            if y["Toss"][turn]["Player"] == str(request.user.username):
                req = data
                outdata = move.move(y, req)
                out = ast.literal_eval(outdata)
                try:
                    update_stat_at_end(request, y, out)
                except Exception as e:
                    print(f"update_stat_at_end {e}")
                y = out
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


def refresh(request, game_id):
    if request.method in ["POST", "GET"]:
        z = get_object_or_404(PitzpalGame, id=game_id)
        y = z.game
        ret = {
            "GameID": game_id,
            "Board": y["Board"],
            "Error": {"Value": 0},
            "Status": y["Status"],
        }
        if y["Status"] != "toss":
            ret["Toss"] = y["Toss"]
            ret["Moves"] = y["Moves"]
        return JsonResponse(ret)


@login_required
def game_list(request):
    # Get all games where the user is player1 or player2
    games = PitzpalGame.objects.filter(
        player1=request.user
    ) | PitzpalGame.objects.filter(player2=request.user)
    return render(request, "home/game_list.html", {"games": games.order_by("-id")})


@login_required
def delete_game(request, game_id):
    if request.method == "POST":
        game = get_object_or_404(PitzpalGame, id=game_id, player1=request.user)
        game.delete()
        messages.success(request, "Game deleted successfully.")
    return redirect("game_list")
