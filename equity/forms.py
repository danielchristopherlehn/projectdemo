from django import forms
from .models import Equity


# Form for registering / editing an equity record.
# Widgets add the CSS class and placeholders so the inputs match the
# styled form used on the assets pages.
class EquityForm(forms.ModelForm):
    class Meta:
        model = Equity
        fields = ['equity_name', 'equity_type', 'amount', 'location']
        widgets = {
            'equity_name': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., Savings Balance 2024'}),
            'equity_type': forms.Select(attrs={'class': 'form-field'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
            'location': forms.Select(attrs={'class': 'form-field'}),
        }
