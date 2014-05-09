from django import forms


class GromacsForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    zip_file = forms.FileField()
