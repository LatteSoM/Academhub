class GradeBookMixin:
    __properties = {}

    def get_properties(self, request):
        """
        Получает id группы из запроса и сохраняет его в словаре properties.
        """
        for property in self.properties:
            self.__properties[property] = request.GET.get(property, None)
    
    def get_form_kwargs(self):
        """
        Добавляет словарь properties в аргументы формы.
        """
        kwargs = super().get_form_kwargs()
        kwargs['properties'] = self.__properties
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.get_properties(request)
        return super().dispatch(request, *args, **kwargs)