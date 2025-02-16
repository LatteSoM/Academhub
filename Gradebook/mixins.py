class GradeBookMixin:
    properties = {}

    def get_properties(self, request):
        """
        Получает id группы из запроса и сохраняет его в словаре properties.
        """
        self.properties['group_id'] = request.GET.get('group_id')
    
    def get_form_kwargs(self):
        """
        Добавляет словарь properties в аргументы формы.
        """
        kwargs = super().get_form_kwargs()
        kwargs['properties'] = self.properties
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.get_properties(request)
        return super().dispatch(request, *args, **kwargs)