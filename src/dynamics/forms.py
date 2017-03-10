from django import forms

from dynamics.models import Dynamic, Box


class DynamicForm(forms.ModelForm):
    class Meta:
        model = Dynamic
        fields = ['box_size', 'number_of_molecules',
                  'number_of_atoms_for_alignment', 'run_alignment', 'run_lqtagrid']

    # def clean(self):
    #     cleaned_data = super(DynamicForm, self).clean()
    #     cleaned_data['number_of_molecules'] = 0
    #     return cleaned_data


class MoleculeForm(forms.Form):
    file = forms.FileField(required=True)
    atoms = forms.CharField(max_length=40)


class IncludeMoreMoleculesForm(forms.Form):
    number_of_molecules = forms.IntegerField()


class RunAlignmentMoleculeForm(forms.Form):
    atoms = forms.CharField(max_length=40)


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['box_dimension_x', 'box_dimension_y', 'box_dimension_z',
                  'box_coordinate_x', 'box_coordinate_y', 'box_coordinate_z',
                  'step', 'probe']
