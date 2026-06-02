from django import forms
from .models import Liability
from assets.models import Asset


class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = [
            'liability_name', 'liability_type', 'lender',
            'principal_amount', 'interest_rate', 'monthly_payment',
            'term_months', 'start_date',
            'location', 'linked_asset', 'notes',
        ]
        # 'form-field' is the css class I use to style all the inputs the same.
        widgets = {
            'liability_name': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., DNB Mortgage'}),
            'liability_type': forms.Select(attrs={'class': 'form-field'}),
            'lender': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., DNB Bank'}),
            'principal_amount': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., 3.5', 'step': '0.01'}),
            'monthly_payment': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
            'term_months': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., 360 for 30 years'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-field', 'type': 'date'}),
            'location': forms.Select(attrs={'class': 'form-field'}),
            'linked_asset': forms.Select(attrs={'class': 'form-field'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-field', 'rows': 2, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only let the user link to one of their own assets.
        if user:
            self.fields['linked_asset'].queryset = Asset.objects.filter(user=user)
        self.fields['linked_asset'].required = False
        self.fields['linked_asset'].empty_label = '--- No linked asset ---'

        # These fields are all optional when adding a liability.
        self.fields['lender'].required = False
        self.fields['monthly_payment'].required = False
        self.fields['term_months'].required = False
        self.fields['start_date'].required = False
        self.fields['notes'].required = False
