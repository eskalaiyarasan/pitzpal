# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render


def home_view(request):
    # You can pass data to the template via a dictionary (context)
    context = {
        "page_title": "Home Page",
        "welcome_message": "Welcome to our site!",
    }
    return render(request, "home/home.html", context)


def new_game(request, numPlayers):
    # You can pass data to the template via a dictionary (context)
    context = {
        "page_title": "New game Page",
        "welcome_message": "Welcome to our site!",
    }
    return render(request, "home/newgame.html", context)
