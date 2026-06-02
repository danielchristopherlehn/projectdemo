from django import forms
from .models import Account, Transaction


class AccountForm(forms.ModelForm):
    # Little checkbox so a brand new account just starts at 0.
    is_new_account = forms.BooleanField(
        required=False,
        label="This is a new account — start at $0.00",
    )

    class Meta:
        model = Account
        fields = ['name', 'account_class', 'account_type', 'currency',
                  'country', 'initial_balance', 'credit_limit',
                  'payment_penalty']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., DNB Main Account'}),
            'account_class': forms.Select(attrs={
                'class': 'form-field', 'id': 'id_account_class'}),
            'account_type': forms.Select(attrs={
                'class': 'form-field', 'id': 'id_account_type'}),
            'currency': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'NOK', 'maxlength': 3}),
            'country': forms.Select(attrs={'class': 'form-field'}),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00',
                'step': '0.01', 'id': 'id_initial_balance'}),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00',
                'step': '0.01', 'id': 'id_credit_limit'}),
            'payment_penalty': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00',
                'step': '0.01', 'id': 'id_payment_penalty'}),
        }

    # Which account types belong to assets and which to liabilities. I use
    # these to stop the user picking a type that doesn't match the class.
    ASSET_TYPES = {'CASH', 'CHECKING', 'SAVINGS', 'E-WALLET'}
    LIABILITY_TYPES = {'CREDIT_CARD', 'OVERDRAFT', 'LINE_OF_CREDIT'}

    def clean(self):
        cleaned_data = super().clean()
        account_class = cleaned_data.get('account_class')
        account_type = cleaned_data.get('account_type')

        # If they ticked "new account" the balance just starts at 0.
        if cleaned_data.get('is_new_account'):
            cleaned_data['initial_balance'] = 0

        # The penalty field can be left empty, treat that as 0.
        if cleaned_data.get('payment_penalty') in (None, ''):
            cleaned_data['payment_penalty'] = 0

        # Asset accounts don't have a credit limit or a penalty fee.
        if account_class == 'CURRENT_ASSET':
            cleaned_data['credit_limit'] = None
            cleaned_data['payment_penalty'] = 0
            if account_type and account_type in self.LIABILITY_TYPES:
                self.add_error('account_type',
                               'This type belongs to liabilities. Choose Cash, Checking, Savings, or Digital Wallet for a Current Asset.')

        # A liability account can't use an asset type.
        if account_class == 'CURRENT_LIABILITY':
            if account_type and account_type in self.ASSET_TYPES:
                self.add_error('account_type',
                               'This type belongs to assets. Choose Credit Card, Overdraft, or Line of Credit for a Current Liability.')

        return cleaned_data


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'account', 'transaction_type', 'category',
                  'description', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-field'}),
            'account': forms.Select(attrs={'class': 'form-field'}),
            'transaction_type': forms.Select(attrs={'class': 'form-field'}),
            'category': forms.Select(attrs={'class': 'form-field'}),
            'description': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'Optional description'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        # I pass the logged in user in so the account dropdown only shows
        # their own accounts.
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['account'].queryset = Account.objects.filter(
                user=user,
                account_class__in=['CURRENT_ASSET', 'CURRENT_LIABILITY']
            )
            self.fields['account'].empty_label = "--- Select Account ---"
        self.fields['category'].required = False
        # Transfers have their own page, so only Revenue/Expense here.
        self.fields['transaction_type'].choices = [
            ('REVENUE', 'Revenue'),
            ('EXPENSE', 'Expense'),
        ]

    # Categories split into income ones and expense ones.
    INCOME_CATEGORIES = {'SALARY', 'DIVIDENDS', 'EXTRAS'}
    EXPENSE_CATEGORIES = {'HOUSEHOLD', 'SERVICES', 'SUBSCRIPTIONS',
                          'ENTERTAINMENT', 'TECHNOLOGY', 'OTHER'}

    def clean(self):
        cleaned_data = super().clean()
        t_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        # A category always has to be chosen.
        if not category:
            self.add_error('category', 'Category is required.')
            return cleaned_data

        # You can't earn revenue into a credit card.
        account = cleaned_data.get('account')
        if account and account.account_class == 'CURRENT_LIABILITY' and t_type == 'REVENUE':
            self.add_error('transaction_type',
                           'A liability account cannot receive revenue. Use a Current Asset account for income.')

        # Make sure the category matches the type (income vs expense).
        if t_type == 'REVENUE' and category in self.EXPENSE_CATEGORIES:
            self.add_error('category',
                           'This category belongs to expenses. Choose Salary, Dividends, or Extras for Revenue.')

        if t_type == 'EXPENSE' and category in self.INCOME_CATEGORIES:
            self.add_error('category',
                           'This category belongs to income. Choose a spending category for Expense.')

        return cleaned_data


class TransferForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-field'})
    )
    source_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        empty_label="--- Select Source Account ---",
        widget=forms.Select(attrs={'class': 'form-field'}),
        label="From Account",
    )
    destination_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        empty_label="--- Select Destination Account ---",
        widget=forms.Select(attrs={'class': 'form-field'}),
        label="To Account",
    )
    amount = forms.DecimalField(
        min_value=0.01, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-field', 'placeholder': 'Optional note'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # You can only send money out of an asset account, but you can
            # send it to any of your accounts (including paying a card).
            assets = Account.objects.filter(
                user=user, account_class='CURRENT_ASSET')
            all_accounts = Account.objects.filter(
                user=user,
                account_class__in=['CURRENT_ASSET', 'CURRENT_LIABILITY']
            )
            self.fields['source_account'].queryset = assets
            self.fields['destination_account'].queryset = all_accounts

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source_account')
        dest = cleaned_data.get('destination_account')
        amount = cleaned_data.get('amount')

        # Can't transfer to the same account you're sending from.
        if source and dest and source == dest:
            raise forms.ValidationError(
                "Source and destination cannot be the same account.")

        # Can't send more than what's in the source account.
        if source and amount:
            if source.initial_balance - amount < 0:
                raise forms.ValidationError(
                    f"Insufficient funds in '{source.name}'. "
                    f"Available: ${source.initial_balance:.2f}"
                )
        return cleaned_data


class PayCardForm(forms.Form):
    # separate from the normal transfer form because paying a card works a bit differently, you pay full balance or just part of it
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-field'})
    )
    source_account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        empty_label="--- Pay from account ---",
        widget=forms.Select(attrs={'class': 'form-field'}),
        label="Pay From",
    )
    card = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        empty_label="--- Select card ---",
        widget=forms.Select(attrs={'class': 'form-field', 'id': 'id_card'}),
        label="Card to Pay",
    )

    pay_full = forms.BooleanField(
        required=False, label="Pay full balance",
        widget=forms.CheckboxInput(attrs={'id': 'id_pay_full'}),
    )
    amount = forms.DecimalField(
        required=False, min_value=0.01, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-field', 'placeholder': '0.00',
            'step': '0.01', 'id': 'id_pay_amount'}),
    )
    # some banks charge a fee when you pay, this lets the user include it or not
    apply_penalty = forms.BooleanField(
        required=False, initial=True, label="Apply bank penalty fee",
        widget=forms.CheckboxInput(attrs={'id': 'id_apply_penalty'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # only show the users own accounts in the dropdowns
            self.fields['source_account'].queryset = Account.objects.filter(
                user=user, account_class='CURRENT_ASSET')
            self.fields['card'].queryset = Account.objects.filter(
                user=user, account_class='CURRENT_LIABILITY')

    def clean(self):
        cleaned_data = super().clean()
        pay_full = cleaned_data.get('pay_full')
        amount = cleaned_data.get('amount')

        # need at least one of these otherwise we dont know how much to pay
        if not pay_full and not amount:
            raise forms.ValidationError(
                "Enter an amount, or tick 'Pay full balance'.")
        return cleaned_data
