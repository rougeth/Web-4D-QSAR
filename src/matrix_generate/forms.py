from django import forms

from matrix_generate.models import MatrixGenerate


class MatrixGenerateForm(forms.ModelForm):
    class Meta:
        model = MatrixGenerate
        fields = ['email', 'name', 'number_of_molecules']


class MoleculeForm(forms.Form):
    file = forms.FileField(required=True)

class BoxForm(forms.Form):
    fields = ['box_dimension_x', 'box_dimension_y', 'box_dimension_z',
        'box_coordinate_x', 'box_coordinate_y', 'box_coordinate_z',
        'coo', 'nh3', 'ch3', 'arc', 'oh', 'nh2', 'arn', 'c_o', 'sh',
        'nh2_arg', 'h2o', 'zn2', 'cl', 'na']