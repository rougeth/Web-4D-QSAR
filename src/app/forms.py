from django import forms

from app.models import Dynamic


class DynamicForm(forms.Form):
    email = forms.EmailField()
    box_size = forms.IntegerField()


class MoleculeForm(forms.Form):
    file = forms.FileField()
