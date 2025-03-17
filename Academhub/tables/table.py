from .column import *
from django_tables2 import tables
from Academhub.utils import getpattern

__all__ = (
    'BaseTable',
    'BaseTable2'
)

class BaseTable(tables.Table):
    # selection = CheckBoxColumn(accessor='pk', orderable=False, verbose_name='')

    edition = ButtonLinkColumn(accessor='pk', text='Изменить', verbose_name='')

    view_detail = ButtonLinkColumn(accessor='pk', text='Просмотреть', verbose_name='')

    def __init__(self, *args, **kwargs):
        # if 'selection' not in self._meta.fields:
        #     self._meta.fields = ('selection',) + self._meta.fields

        super().__init__(*args, **kwargs)

        model = self._meta.model

        if 'edition' not in self._meta.fields:
            self._meta.fields += ('edition', )

        if 'view_detail' not in self._meta.fields:
            self._meta.fields += ('view_detail', )

        change_url = getpattern(model, 'change')
        detail_url = getpattern(model, 'detail')

        self.columns['edition'].column._set_url_name(change_url)
        self.columns['view_detail'].column._set_url_name(detail_url)

class BaseTable2(tables.Table):
    edition = ButtonLinkColumn(accessor='pk', text='Изменить', verbose_name='')
    view_detail = ButtonLinkColumn(accessor='pk', text='Просмотреть', verbose_name='')

    def __init__(self, *args, **kwargs):
        if 'edition' not in self._meta.fields:
            self._meta.fields += ('edition',)

        if 'view_detail' not in self._meta.fields:
            self._meta.fields += ('view_detail',)

        super().__init__(*args, **kwargs)

        model = self._meta.model

        detail_url = getpattern(model, 'detail')

        self.columns['view_detail'].column._set_url_name(detail_url)