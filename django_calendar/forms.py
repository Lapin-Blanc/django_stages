from django.forms import ModelForm
from .models import Convention

class ConventionForm(ModelForm):
    class Meta:
        model = Convention
        fields = ['place', 'stage', 'type_stage', 'teacher']
