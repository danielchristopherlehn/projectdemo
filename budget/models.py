from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from .countries import COUNTRY_CHOICES


class Account(models.Model):
    CLASS_CHOICES = [
        ('LIQUID', 'Liquidity (Cash & Banks)'),
        ('DEBT', 'Liabilities (Credit & Loans)'),
    ]

    ACCOUNT_TYPES = [
        ('Liquidity', (
            ('CHECKING', 'Checking Account'),
            ('SAVINGS', 'Savings Account'),
            ('CASH', 'Physical Cash'),
            ('E-WALLET', 'Digital Wallet (PayPal/Revolut)'),
        )),
        ('Liabilities', (
            ('CREDIT_CARD', 'Credit Card'),
            ('OVERDRAFT', 'Bank Overdraft'),
            ('LINE_OF_CREDIT', 'Line of Credit'),
        )),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, help_text="e.g., DNB Main Account")
    account_class = models.CharField(
        max_length=10, choices=CLASS_CHOICES, default='LIQUID'
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(
        max_length=3, default='NOK', help_text="e.g., NOK, USD, EUR"
    )
    country = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no'
    )

    initial_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_country_display()})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
    ]

    CATEGORY_CHOICES = [
        ('SALARY', 'Salary'),
        ('DIVIDENDS', 'Dividends'),
        ('EXTRAS', 'Extras / Other Income'),
        ('HOUSEHOLD', 'Household & Supplies'),
        ('SERVICES', 'Utilities & Services'),
        ('SUBSCRIPTIONS', 'Subscriptions'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('TECHNOLOGY', 'Technology & Tools'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions')

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Select the funding source or debt account for this transaction."
    )

    date = models.DateField()
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255)

    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"{self.date} | {self.get_transaction_type_display()} | {self.amount}"
