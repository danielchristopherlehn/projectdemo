from django.db import models
from django.contrib.auth.models import User
import uuid


class Project(models.Model):

    CALCULATOR_TYPES = [
        ('loan', 'Loan Calculator'),
        ('mortgage', 'Mortgage Calculator'),
        ('rent_vs_own', 'Rent vs Own'),
        ('budget', 'Personal Budget'),
    ]

    project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calculator_type = models.CharField(max_length=50, choices=CALCULATOR_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name