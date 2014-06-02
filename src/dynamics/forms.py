from django import forms


class DynamicForm(forms.Form):
    email = forms.EmailField()
    box_size = forms.IntegerField()
    file = forms.FileField()
