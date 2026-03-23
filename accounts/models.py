from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    currency = models.CharField(max_length=50, default="NOK")
    country = models.CharField(max_length=50, blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"
