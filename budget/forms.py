from django import forms
from .models import Account, Transaction


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name',
            'account_class',
            'account_type',
            'currency',
            'country',
            'initial_balance',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., DNB Debit Account',
                'class': 'form-control',
            }),
            'account_class': forms.Select(attrs={
                'class': 'form-control',
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'currency': forms.TextInput(attrs={
                'placeholder': 'USD',
                'class': 'form-control',
            }),
            'country': forms.Select(attrs={
                'class': 'form-control',
            }),
            'initial_balance': forms.NumberInput(attrs={
                'placeholder': 'Starting Balance',
                'class': 'form-control',
            }),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'date',
            'transaction_type',
            'category',
            'description',
            'amount',
            'account',
        ]

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'Optional description',
                'class': 'form-control',
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control',
            }),
            'account': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['account'].empty_label = "--- Select Funding Source ---"