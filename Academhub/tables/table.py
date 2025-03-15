from .column import *
from django_tables2 import tables

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

        url = self._meta.model.get_urls()

        if 'edition' not in self._meta.fields:
            self._meta.fields += ('edition', )

        if 'view_detail' not in self._meta.fields:
            self._meta.fields += ('view_detail', )

        self.columns['edition'].column._set_url_name(url['url_update'])
        self.columns['view_detail'].column._set_url_name(url['url_detail'])

class BaseTable2(tables.Table):
    edition = ButtonLinkColumn(accessor='pk', text='Изменить', verbose_name='')
    view_detail = ButtonLinkColumn(accessor='pk', text='Просмотреть', verbose_name='')

    def __init__(self, *args, **kwargs):
        if 'edition' not in self._meta.fields:
            self._meta.fields += ('edition',)

        if 'view_detail' not in self._meta.fields:
            self._meta.fields += ('view_detail',)

        super().__init__(*args, **kwargs)

        url = self._meta.model.get_urls()

        self.columns['view_detail'].column._set_url_name(url['url_detail'])