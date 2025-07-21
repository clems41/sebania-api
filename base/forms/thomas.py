from django import forms


class UploadVocalForm(forms.Form):
    file = forms.FileField()
    date = forms.DateField()