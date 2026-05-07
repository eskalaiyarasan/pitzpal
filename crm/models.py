import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    ph = models.BigIntegerField(default=0)
    dob = models.DateField(default=datetime.date(2000, 1, 1))
    email = models.EmailField(unique=True)
    rating = models.IntegerField(default=100)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
