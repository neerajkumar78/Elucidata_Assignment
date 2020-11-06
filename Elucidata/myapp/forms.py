from django import forms

class FileUpload(forms.Form):
	files = forms.FileField()