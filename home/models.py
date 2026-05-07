from django.conf import settings
from django.db import models


# Create your models here.
class Game(models.Model):
    white_player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="A_games"
    )
    black_player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="B_games"
    )
    fen = models.CharField(max_length=255, default="startpos")  # Current board state
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MatchSeek(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    time_control = models.CharField(max_length=20)  # e.g., "10+0"
    created_at = models.DateTimeField(auto_now_add=True)
