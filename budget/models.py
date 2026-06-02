from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from .countries import COUNTRY_CHOICES


# An Account is one of the user's money accounts. It can be an asset (money you
# have, like cash or savings) or a liability (money you owe, like a credit card).
class Account(models.Model):
    CLASS_CHOICES = [
        ('CURRENT_ASSET', 'Current Asset'),
        ('CURRENT_LIABILITY', 'Current Liability'),
    ]

    # Grouped so the dropdown shows assets and liabilities separately.
    ACCOUNT_TYPES = [
        ('Current Assets', (
            ('CASH', 'Physical Cash'),
            ('CHECKING', 'Checking Account'),
            ('SAVINGS', 'Savings Account'),
            ('E-WALLET', 'Digital Wallet (PayPal/Revolut)'),
        )),
        ('Current Liabilities', (
            ('CREDIT_CARD', 'Credit Card'),
            ('OVERDRAFT', 'Bank Overdraft'),
            ('LINE_OF_CREDIT', 'Line of Credit'),
        )),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_class = models.CharField(
        max_length=20, choices=CLASS_CHOICES, default='CURRENT_ASSET')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    currency = models.CharField(max_length=3, default='NOK')
    country = models.CharField(
        max_length=2, choices=COUNTRY_CHOICES, default='no')
    # For an asset this is how much money is in it. For a credit card it is
    # how much you currently owe.
    initial_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    # Only used by credit cards / lines of credit - the most you can borrow.
    credit_limit = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    # A fee the bank charges every time you pay this card off.
    payment_penalty = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, blank=True,
        help_text="Fee the bank charges each time you pay this card/liability.")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Asset accounts shouldn't have a credit limit set.
        from django.core.exceptions import ValidationError
        if self.account_class == 'CURRENT_ASSET' and self.credit_limit is not None:
            raise ValidationError(
                {'credit_limit': 'Credit limit only applies to liability accounts.'})

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


# A Transaction is one movement of money: income (revenue), spending (expense),
# or a transfer between two accounts.
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
    ]

    CATEGORY_CHOICES = [
        ('Income', (
            ('SALARY', 'Salary'),
            ('DIVIDENDS', 'Dividends'),
            ('EXTRAS', 'Extras / Other Income'),
        )),
        ('Expenses', (
            ('HOUSEHOLD', 'Household & Supplies'),
            ('SERVICES', 'Utilities & Services'),
            ('SUBSCRIPTIONS', 'Subscriptions'),
            ('ENTERTAINMENT', 'Entertainment'),
            ('TECHNOLOGY', 'Technology & Tools'),
            ('OTHER', 'Other'),
        )),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name='transactions')
    # Only used for transfers - the account the money goes to.
    destination_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incoming_transfers')
    date = models.DateField()
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, blank=True, default='')
    description = models.CharField(max_length=255, blank=True, default='')
    # Amount always has to be at least 0.01 (no zero or negative amounts).
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f"{self.date} | {self.get_transaction_type_display()} | {self.amount}"
