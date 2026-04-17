from django.db import models
from django.contrib.auth.models import User
# <-- Import the list from your new file
from assets.countries import COUNTRY_CHOICES


class Asset(models.Model):
    ASSET_TYPE_CHOICES = [

        # Permafrost assets / FIXED ASSETS
        ('Property & Land', 'Property & Land'),
        ('Equipment & Machinery', 'Equipment & Machinery'),
        ('Furniture', 'Furniture'),
        ('Long-Term Investments', 'Long-Term Investments'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_assets')
    asset_name = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    country = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    value_estimate = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    purchase_year = models.PositiveIntegerField()
    active_Status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.asset_name} ({self.asset_type})"
