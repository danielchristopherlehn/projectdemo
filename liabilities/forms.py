from django import forms
from .models import Liability


class LiabilityForm(forms.ModelForm):
    class Meta:
        model = Liability
        fields = ['liability_name', 'liability_type', 'principal_amount',
                  'interest_rate', 'location', 'linked_asset']
