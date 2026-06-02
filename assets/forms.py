from django import forms
from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_name', 'asset_type', 'country',
            'purchase_price', 'value_estimate', 'purchase_year',
            'active_Status', 'notes',
        ]

        widgets = {
            'asset_name': forms.TextInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., Oslo Apartment'}),
            'asset_type': forms.Select(attrs={'class': 'form-field'}),
            'country': forms.Select(attrs={'class': 'form-field'}),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00', 'step': '0.01'}),
            'value_estimate': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': '0.00 (optional)', 'step': '0.01'}),
            'purchase_year': forms.NumberInput(attrs={
                'class': 'form-field', 'placeholder': 'e.g., 2022'}),
            'active_Status': forms.CheckboxInput(),
            'notes': forms.Textarea(attrs={
                'class': 'form-field', 'rows': 2, 'placeholder': 'Optional notes'}),
        }

    def __init__(self, *args, **kwargs):
        # The view passes a user in, but the asset form doesn't need it.
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # These two fields are optional.
        self.fields['value_estimate'].required = False
        self.fields['notes'].required = False
