from Academhub.tables import BaseTable
import django_tables2 as table
from Academhub.models import Curriculum

__all__ = (
    "Curriculum"
)

class CurriculumTable(BaseTable):
    class Meta:
        model = Curriculum
        pagination_by = 30
        fields = ('qualification', 'admission_year')
