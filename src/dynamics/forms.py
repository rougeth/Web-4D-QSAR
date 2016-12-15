from django import forms

from dynamics.models import Dynamic


class DynamicForm(forms.ModelForm):
    class Meta:
        model = Dynamic
        fields = ['email', 'name', 'box_size', 'number_of_molecules',
                  'number_of_atoms_for_alignment']


class MoleculeForm(forms.Form):
    file = forms.FileField(required=True)
    atoms = forms.CharField(max_length=40)
