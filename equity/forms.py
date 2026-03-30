from django import forms
from .models import Equity


class EquityForm(forms.ModelForm):
    class Meta:
        model = Equity
        fields = ['equity_name', 'equity_type', 'amount', 'location']
