from django.db import models
from django.contrib.auth.models import User
from assets.countries import COUNTRY_CHOICES


# A long term asset the user owns, like a house, a car or an investment.
class Asset(models.Model):

    ASSET_TYPE_CHOICES = [
        ('Property & Land', 'Property & Land'),
        ('Vehicles', 'Vehicles'),
        ('Equipment & Machinery', 'Equipment & Machinery'),
        ('Furniture & Fixtures', 'Furniture & Fixtures'),
        ('Long-Term Investments', 'Long-Term Investments'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_assets')
    asset_name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    country = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    # What I paid for it, and what I think it's worth now (user has liberty to put or not).
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2)
    value_estimate = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    purchase_year = models.PositiveIntegerField()
    # Whether I still own it / it's still active.
    active_status = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.asset_name} ({self.asset_type})"
