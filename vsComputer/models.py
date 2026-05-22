# Create your models here.
import uuid

from django.conf import settings
from django.db import models


class PitzpalGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="games_p1"
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    # This stores the "Game" schema JSON
    game = models.JSONField()

    def save(self, *args, **kwargs):
        # 1. Ensure 'game' is a dictionary (not a string)
        if isinstance(self.game, dict):
            # 2. Update the JSON property to match the Model ID
            # We convert UUID to string because JSON doesn't have a UUID type
            self.game["GameID"] = str(self.id)

        # 3. Call the actual save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Game {self.id} - Turn: {self.game}"
