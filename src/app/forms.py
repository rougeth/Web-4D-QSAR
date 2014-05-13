from django import forms

from app.models import Dynamic


class DynamicForm(forms.Form):
    email = forms.EmailField()

    box_size_x = forms.IntegerField()
    box_size_y = forms.IntegerField()
    box_size_z = forms.IntegerField()


class DynamicFileForm(forms.Form):
    file = forms.FileField()
