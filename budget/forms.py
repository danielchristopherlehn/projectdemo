from django import forms
from .models import Transaction, Account


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        # FIXED: Changed 'balance' to 'initial_balance'
        fields = ['name', 'account_class', 'account_type',
                  'currency', 'country', 'initial_balance']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., DNB Debit Account', 'class': 'form-control'}),
            'account_class': forms.Select(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'placeholder': 'USD', 'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            # FIXED: Changed 'balance' to 'initial_balance'
            'initial_balance': forms.NumberInput(attrs={'placeholder': 'Starting Balance', 'class': 'form-control'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'category',
                  'description', 'amount', 'account']
        # ... keep your existing widgets for styling ...

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['account'].empty_label = "--- Select Funding Source ---"
