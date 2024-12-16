from django import forms
from django.contrib import admin
from .models import UserProfile
import uuid

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'nip']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.instance.nip:
            self.fields['nip'].initial = str(uuid.uuid4().int)[:8]

    def clean_nip(self):
        nip = self.cleaned_data.get('nip')
        if len(nip) != 8:
            raise forms.ValidationError('O NIP deve ter exatamente 8 dígitos.')
        return nip
