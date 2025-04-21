import json
from django import forms
from ..widgets import ExcelRangeWidget, DictCoordsWidget, TupleCoordsWidget

__all__ = (
    'ExcelField',
    'DictCoordsField',
    'TupleCoordsField',
)

class ExcelField(forms.MultiValueField):
    def __init__(self, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(),
        )
        
        self.widget = ExcelRangeWidget()

        super().__init__(fields, **kwargs)
    
    def compress(self, data_list):
        """Преобразует список ['Sheet1', 'A1:B2'] в {'A1:B2': 'Sheet1'}"""
        if data_list and all(data_list):
            return {data_list[1].upper(): data_list[0]}
        return None

class TupleCoordsField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', TupleCoordsWidget())
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """Преобразует JSON-строку в кортеж вида ('range1', 'range2', ..., 'sheet')"""
        value = super().clean(value)
        if not value:
            return ""
        
        try:
            data = json.loads(value)
            if not isinstance(data, list) or len(data) < 1:
                raise forms.ValidationError("Неверный формат данных диапазона")
            
            sheet = data[-1] if data else ""
            ranges = data[:-1] if len(data) > 1 else []
            
            for range_value in ranges:
                if not isinstance(range_value, str) or not range_value:
                    raise forms.ValidationError("Диапазоны должны быть непустыми строками")
            
            return tuple(ranges + [sheet])
        except (json.JSONDecodeError, TypeError):
            raise forms.ValidationError("Неверный формат данных диапазона")

class DictCoordsField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', DictCoordsWidget())
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """Преобразует JSON-строку в словарь вида {'cell': 'sheet'}"""
        value = super().clean(value)
        if not value:
            return {}
        
        try:
            data = json.loads(value)
            result = {}
            for item in data:
                if item.get('cell') and item.get('sheet'):
                    result[item['cell']] = item['sheet']
            return result
        except (json.JSONDecodeError, TypeError):
            raise forms.ValidationError("Неверный формат данных диапазон")