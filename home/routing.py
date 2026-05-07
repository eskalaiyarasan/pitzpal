from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/matchmaking/$", consumers.MatchmakingConsumer.as_async()),
    # Path for the actual game moves (using the game ID)
    re_path(r"ws/game/(?P<game_id>\w+)/$", consumers.GameConsumer.as_asgi()),
]
