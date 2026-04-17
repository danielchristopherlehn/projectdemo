from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_name',
            'asset_type',
            'country',
            'purchase_price',
            'value_estimate',
            'purchase_year',
            'active_Status'
        ]
        # Optional: Add styling to the form fields
        widgets = {
            'asset_name': forms.TextInput(attrs={'style': 'width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc;'}),
            'country': forms.Select(attrs={'style': 'width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc;'}),
        }
