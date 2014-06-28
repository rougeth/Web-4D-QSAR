from django import forms

from dynamics.models import Dynamic


class DynamicForm(forms.ModelForm):
    class Meta:
        model = Dynamic
        fields = ['email', 'box_size']


class MoleculeForm(forms.Form):
    file = forms.FileField()
