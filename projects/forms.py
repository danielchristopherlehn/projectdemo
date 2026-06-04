from django import forms
from assets.models import Asset
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'calculator_type', 'linked_asset']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['linked_asset'].queryset = Asset.objects.filter(
                user=user,
                asset_type='Property & Land',
                active_status=True
            )
        self.fields['linked_asset'].required = False
        self.fields['linked_asset'].empty_label = "No — I'll enter data manually"
