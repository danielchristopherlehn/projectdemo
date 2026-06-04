from django.db import models
from django.contrib.auth.models import User
from assets.models import Asset
from .countries import COUNTRY_CHOICES


# A long term liability, basically a loan the user has to pay back over time
# (mortgage, car loan, student loan, etc).
class Liability(models.Model):

    LIABILITY_TYPE_CHOICES = [
        ('Mortgage', 'Mortgage'),
        ('Car Loan', 'Car Loan'),
        ('Student Loan', 'Student Loan'),
        ('Personal Loan', 'Personal Loan'),
        ('Business Loan', 'Business Loan'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liability_name = models.CharField(max_length=100)
    liability_type = models.CharField(
        max_length=50, choices=LIABILITY_TYPE_CHOICES)
    # How much was borrowed and the yearly interest rate.
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="e.g. 5.5 for 5.5%")
    # Optional extra info about the loan.
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    term_months = models.PositiveIntegerField(
        null=True, blank=True, help_text="Total loan term in months, e.g. 360 for 30 years")
    start_date = models.DateField(null=True, blank=True)
    lender = models.CharField(
        max_length=100, blank=True, default='', help_text="Bank or institution name")
    location = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    # A loan can be linked to an asset it paid for (e.g. a mortgage -> a house).
    linked_asset = models.ForeignKey(
        Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name='liabilities')
    notes = models.TextField(blank=True, default='')

# Literally used cuz otherwise Django admin reads "Liabilitys" lol
    class Meta:
        verbose_name_plural = "Liabilities"

    def __str__(self):
        return f"{self.liability_name} ({self.principal_amount})"
