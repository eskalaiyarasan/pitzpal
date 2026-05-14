import error
import game
import movereq


def move(game_in, data):
    ret = {}
    x = game.game.from_json(game_in)
    req = movereq.movereq.from_json(data)
    try:
        ret = x.move(req)
    except Exception as e:
        print(f"exception : move{data} : {e}")
    return str(ret)
