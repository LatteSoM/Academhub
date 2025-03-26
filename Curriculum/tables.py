from Academhub.tables import BaseTable
from Academhub.models import Curriculum

__all__ = (
    "Curriculum"
)

class CurriculumTable(BaseTable):
    class Meta:
        model = Curriculum
        pagination_by = 10
        fields = ('qualification', 'admission_year')
