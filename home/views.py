# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Game


def home_view(request):
    # You can pass data to the template via a dictionary (context)
    context = {
        "page_title": "Home Page",
        "welcome_message": "Welcome to our Bootstrap-powered site!",
    }
    return render(request, "home/home.html", context)


@login_required
def lobby(request):
    return render(request, "home/lobby.html")


@login_required
def game_room(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    # Determine if user is White or Black
    user_color = "white" if request.user == game.white_player else "black"

    return render(request, "chess/game.html", {"game": game, "user_color": user_color})
