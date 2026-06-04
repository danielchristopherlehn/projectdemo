from django import forms

# Getting from the same folder the model asset
from .models import Asset

# Here we create a form for the asset model


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_name', 'asset_type', 'country',
            'purchase_price', 'value_estimate', 'purchase_year',
            'active_status', 'notes',
        ]
        # Above we specified fields (characteristics of the [Asset])
        # This is what the user will fill out

        # The widgets method is usefull for HTML styling.
        # Used to add CSS classes and placeholders, otherwise it collapses
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
            'active_status': forms.CheckboxInput(),
            'notes': forms.Textarea(attrs={
                'class': 'form-field', 'rows': 2, 'placeholder': 'Optional notes'}),
        }
