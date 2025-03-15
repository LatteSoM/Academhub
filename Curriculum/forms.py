import os
from django import forms
from .parser_for_plx import RUP_parser

class GetPlxForm(forms.Form):
    file = forms.FileField(label="Перетащите файл")

    parser = RUP_parser()

    def clean(self):
        super().clean()

        result = self.cleaned_data.get('file')

        if result:
            file_extension = os.path.splitext(result.name)[1]

            if file_extension.lower() != '.plx':
                raise forms.ValidationError("Файл должен быть в формате .plx")
        
            self.get_file_data(result)
    
    def get_file_data(self, file):

        self.parser.add_file(file)
        self.parser.get_plan()
    
    def save(self):
        pass
    
        