import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    ph = models.BigIntegerField(default=0)
    dob = models.DateField(default=datetime.date(2000, 1, 1))
    email = models.EmailField(unique=True)
    rating = models.IntegerField(default=100)
    wins = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username


# ✅ Friend Request Model
class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="received_friend_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    # ✅ Add STATUS FIELD here
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"

    # ✅ Add Meta class INSIDE the model
    class Meta:
        unique_together = ("from_user", "to_user")


class Friends(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="friends_obj"
    )
    friends_list = models.ManyToManyField(User, blank=True, related_name="friends_with")

    def __str__(self):
        return f"{self.user.username}'s Friends"


# ✅ Add this Signal at the bottom of the file
@receiver(post_save, sender=User)
def create_user_friends(sender, instance, created, **kwargs):
    if created:
        Friends.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_friends(sender, instance, **kwargs):
    # This ensures that if for some reason the friends_obj doesn't exist, it gets created
    if not hasattr(instance, "friends_obj"):
        Friends.objects.create(user=instance)
    instance.friends_obj.save()
