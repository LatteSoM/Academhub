from django_tables2 import TemplateColumn, tables

from Academhub.models import Curriculum, ReleaseFromCurriculum, Button
from Academhub.tables import BaseTable
from Academhub.tables.column import ButtonLinkColumn  # Import ButtonLinkColumn
from Academhub.utils import getpattern, getpermission


class CurriculumTable(BaseTable):  # Inherit from BaseTable
    # Define view_detail column (url_name will be set in __init__)
    view_detail = ButtonLinkColumn(
        accessor='pk',
        text='Просмотреть',
        verbose_name=''
    )

    # Add a delete column using TemplateColumn
    delete = TemplateColumn(
        template_code='''
            <button class="btn btn-danger btn-sm"
                    onclick="confirmDelete('{% url 'curriculum_delete' pk=record.pk %}', '{{ record.qualification.name }}', '{{ record.admission_year }}')">
                Удалить
            </button>
        ''',
        verbose_name="",
        orderable=False,
        attrs={
             "th": {"class": "no-header"},
             "td": {"class": "actions-column"} # Keep similar styling if needed
         }
    )

    # Add __init__ to set the correct URL name after BaseTable.__init__ runs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly set the URL name for the view_detail button
        self.columns['view_detail'].column._set_url_name('curriculum_preview')

    class Meta:
        model = Curriculum
        # Add view_detail, edition (from BaseTable), and delete to fields
        fields = ('qualification', 'admission_year', 'basis_of_admission', 'view_detail', 'edition', 'delete')
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-bordered table-hover"}

    # render_actions method is no longer needed


class ReleaseFromCurriculumTable(BaseTable):
    qualification = tables.Column(accessor='curriculum.qualification_name',
        verbose_name='Квалификация')
    study_year = tables.Column(accessor='study_year', verbose_name='Учебный год')
    course = tables.Column(accessor='course',  verbose_name='Курс')

    buttons = [
        Button(
            id='add',
            name='Добавить',
            link_name=getpattern(ReleaseFromCurriculum, 'add'),
            permission=getpermission('ReleaseFromCurriculum', 'create_group_student'),
        )
    ]

    class Meta:
        model = ReleaseFromCurriculum
        paginate_by = 10
        fields = ('qualification', 'study_year', 'course')