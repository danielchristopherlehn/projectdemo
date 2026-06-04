from django import forms
from .models import LoanData, MortgageData, RentVsOwnData


class LoanDataForm(forms.ModelForm):
    class Meta:
        model = LoanData
        fields = ['principal', 'rate', 'years', 'start_year']
        widgets = {
            'principal': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '5.00', 'step': '0.01'}),
            'years': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '5'}),
            'start_year': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '2025'}),
        }


class MortgageDataForm(forms.ModelForm):
    class Meta:
        model = MortgageData
        fields = ['price', 'down_payment', 'rate', 'years', 'start_year']
        widgets = {
            'price': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'down_payment': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '5.00', 'step': '0.01'}),
            'years': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '25'}),
            'start_year': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '2025'}),
        }


class RentVsOwnDataForm(forms.ModelForm):
    class Meta:
        model = RentVsOwnData
        fields = ['rent', 'rent_increase', 'price', 'down_payment', 'rate', 'years', 'start_year']
        widgets = {
            'rent': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'rent_increase': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '3.00', 'step': '0.01'}),
            'price': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'down_payment': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '0.00', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '5.00', 'step': '0.01'}),
            'years': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '10'}),
            'start_year': forms.NumberInput(attrs={
                'class': 'calc-input', 'placeholder': '2025'}),
        }
