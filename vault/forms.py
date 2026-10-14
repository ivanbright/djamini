from django import forms
from django.contrib.auth.models import Group

from .models import License


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = ('name', 'vendor', 'key', 'notes')
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class LicenseAccessForm(forms.Form):
    blocked_groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Groups you tick lose access to this license.',
    )
