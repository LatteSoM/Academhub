from django_filters import FilterSet, CharFilter
from Curriculum.models import CustomUser, PermissionProxy, GroupProxy


class UserFilter(FilterSet):
    """
    Фильтр для пользователей.
    """
    search = CharFilter(method='filter_search')

    class Meta:
        model = CustomUser
        fields = ['search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(email__icontains=value)


class PermissionFilter(FilterSet):
    """
    Фильтр для прав доступа.
    """
    search = CharFilter(method='filter_search')

    class Meta:
        model = PermissionProxy
        fields = ['search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(codename__icontains=value)


class GroupFilter(FilterSet):
    """
    Фильтр для групп.
    """
    search = CharFilter(method='filter_search')

    class Meta:
        model = GroupProxy
        fields = ['search']

    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)