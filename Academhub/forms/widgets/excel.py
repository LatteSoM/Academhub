import re
import json
from django.forms import widgets as wid

__all__ = (
    'ExcelRangeWidget',
    'DictCoordsWidget',
    'TupleCoordsWidget',
    'ExcelMultiCoordsWidget',
)
 
class ExcelCellWidget(wid.TextInput):
    pattern = r'^[A-Za-z]{1,3}\d+(?::[A-Za-z]{1,3}\d+)?$'
    
    regex = re.compile(pattern)
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'excel_cell',
            'placeholder': 'Ячейка(и)',
            'pattern': self.pattern,
            'title': 'Допустимые форматы: A1 или B1:C10',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class ExcelRangeWidget(wid.MultiWidget):
    template_name = 'widgets/excel_range.html'

    def __init__(self, attrs = None):
        attrs_select = {
            'placeholder': 'Sheet1'
        }

        widgets = (
            wid.TextInput(attrs=attrs_select),
            ExcelCellWidget()
        )

        super().__init__(widgets, attrs)
    
    def decompress(self, value):
        """Распаковывает словарь {'A1:B2': 'Sheet1'} в ['Sheet1', 'A1:B2']"""
        if value:
            cell_range, sheet = next(iter(value.items()))
            return [sheet, cell_range]
        return [None, None]
    
    def value_from_datadict(self, data, files, name):
        """Собирает значения для двух полей"""
        return [
            data.get(f'{name}_0'),  # sheet
            data.get(f'{name}_1')   # cell_range
        ]

class ExcelMultiCoordsWidget(wid.MultiWidget):
    template_name = 'widgets/excel_multi_coords.html'
    
    def __init__(self, attrs=None):
        attrs_select = {
            'placeholder': 'Sheet1'
        }
        
        _widgets = [
            wid.HiddenInput(),  # Основное поле для JSON
            wid.TextInput(attrs=attrs_select),
            wid.TextInput(attrs={'placeholder': 'Введите ячейку'}),  # Поле ввода
        ]
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, dict):
                return [json.dumps(value), next(iter(value.values())) if value else '', '']
            elif isinstance(value, (list, tuple)):
                return [json.dumps(dict(zip(value[:-1], [value[-1]]*len(value[:-1])))), value[-1], '']
        return [json.dumps({}), '', '']

class DictCoordsWidget(wid.Widget):
    template_name = "widgets/dict_coords_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        parsed_value = self.parse_value(value)
        # Преобразуем значение в JSON-строку для hidden input
        context['widget']['json_value'] = json.dumps(parsed_value)
        context['widget']['value'] = parsed_value
        return context

    def parse_value(self, value):
        """Парсит входное значение в список словарей для шаблона"""
        if value is None or value == '':
            return []
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                # Если это словарь, преобразуем в список словарей
                if isinstance(parsed, dict):
                    return [{'sheet': k, 'range': v} for k, v in parsed.items()]
                return parsed
            except json.JSONDecodeError:
                return []
        return value


class TupleCoordsWidget(wid.Widget):
    template_name = "widgets/tuple_coords_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        parsed_value = self.parse_value(value)
        context['widget']['json_value'] = json.dumps(parsed_value)
        context['widget']['value'] = parsed_value
        return context

    def parse_value(self, value):
        """Парсит входное значение в список словарей [{'cell': 'B20', 'sheet': 'Sheet2'}, ...]"""
        if value is None or value == '':
            return []
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return []
            except json.JSONDecodeError:
                return []
        if isinstance(value, dict):
            return [{'cell': k, 'sheet': v} for k, v in value.items()]
        return value
