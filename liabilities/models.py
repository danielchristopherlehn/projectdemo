from django.db import models
from django.contrib.auth.models import User
from assets.models import Asset
from .countries import COUNTRY_CHOICES


class Liability(models.Model):
    LIABILITY_TYPES = [
        ('Mortgage', 'Mortgage'),
        ('Car Loan', 'Car Loan'),
        ('Student Loan', 'Student Loan'),
        ('Credit Card', 'Credit Card Debt'),
        ('Other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liability_name = models.CharField(max_length=100)
    liability_type = models.CharField(max_length=50, choices=LIABILITY_TYPES)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="e.g. 5.5 for 5.5%")
    location = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    linked_asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name='liabilities')

    class Meta:
        verbose_name_plural = "Liabilities"

    def __str__(self):
        return f"{self.liability_name} (${self.principal_amount})"
