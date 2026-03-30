from django.db import models
from django.contrib.auth.models import User
from .countries import COUNTRY_CHOICES


class Equity(models.Model):
    EQUITY_TYPES = [
        ('Initial Capital', 'Initial Capital / Savings'),
        ('Retained Earnings', 'Retained Earnings (Saved Income)'),
        ('Appreciation', 'Asset Appreciation'),
        ('Inheritance', 'Inheritance / Gift'),
        ('Other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equity_name = models.CharField(
        max_length=100, help_text="e.g., Savings Account Balance 2024")
    equity_type = models.CharField(max_length=50, choices=EQUITY_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Equities"

    def __str__(self):
        return f"{self.equity_name} (${self.amount})"
