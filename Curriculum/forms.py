from django import forms
import os

class GetPlxForm(forms.Form):
    file = forms.FileField(label="Перетащите файл")

    def clean(self):
        super().clean()

        result = self.cleaned_data.get('file')

        if result:
            file_extension = os.path.splitext(result.name)[1]

            if file_extension.lower() != '.plx':
                raise forms.ValidationError("Файл должен быть в формате .plx")
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.file.save(instance.name, self.cleaned_data.get('file'))

        