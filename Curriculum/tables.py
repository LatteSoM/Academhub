import django_tables2 as tables
from django.urls import reverse_lazy
from django.utils.html import format_html
from Academhub.models import Curriculum


class CurriculumTable(tables.Table):
    actions = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name="",
        attrs={
            "th": {"class": "no-header"},
            "td": {"class": "actions-column"}
        }
    )

    class Meta:
        model = Curriculum
        fields = ('qualification', 'admission_year', 'basis_of_admission')
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-bordered table-hover"}

    def render_actions(self, record):
        preview_url = reverse_lazy('curriculum_preview', kwargs={'pk': record.pk})
        delete_url = reverse_lazy('curriculum_delete', kwargs={'pk': record.pk})

        return format_html(
            '''
            <div class="btn-group" role="group">
                <a href="{}" class="btn btn-info btn-sm">Просмотреть</a>
                <button class="btn btn-danger btn-sm" 
                        onclick="confirmDelete('{}', '{}', '{}')">Удалить</button>
            </div>
            ''',
            preview_url,
            delete_url,
            record.qualification.name,
            record.admission_year
        )
