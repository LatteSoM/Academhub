import django_tables2 as tables
from django.utils.html import format_html


class ActionColumn(tables.Column):
    """
    Колонка действий.
    """

    def __init__(self, actions, *args, **kwargs):
        self.actions = actions
        super().__init__(*args, **kwargs)

    def render(self, value, record):
        buttons = []
        for action in self.actions:
            if 'check' in action:
                if action['check'](record):
                    buttons.append(
                        f'<a href="{record.get_absolute_url().replace("detail", action["url"])}" class="btn btn-primary">{action["name"]}</a>')
            else:
                buttons.append(
                    f'<a href="{record.get_absolute_url().replace("detail", action["url"])}" class="btn btn-primary">{action["name"]}</a>')
        return format_html(' '.join(buttons))