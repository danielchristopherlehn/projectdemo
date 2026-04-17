from django.db import models
from django.contrib.auth.models import User
from assets.models import Asset
import uuid


class Project(models.Model):

    CALCULATOR_TYPES = [
        ('loan', 'Loan Calculator'),
        ('mortgage', 'Mortgage Calculator'),
        ('rent_vs_own', 'Rent vs Own'),
    ]

    project_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calculator_type = models.CharField(max_length=50, choices=CALCULATOR_TYPES)
    linked_asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Optionally link a real asset you own to pre-fill calculator fields."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Report(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="reports")
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for {self.project.name}"
