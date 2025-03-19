from django.db.models import Q
from django import forms
from Academhub.models import CustomUser, GroupProxy, PermissionProxy
from django.contrib.contenttypes.models import ContentType
from django_filters import FilterSet, CharFilter, BooleanFilter, ModelMultipleChoiceFilter, ModelChoiceFilter

class UserFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')
    
    is_staff = BooleanFilter(field_name='is_staff', label='Персонал?',
        widget = forms.CheckboxInput()
    )

    is_teacher = BooleanFilter(field_name='is_teacher', label='Учитель?',
        widget = forms.CheckboxInput(
            attrs={
                "style": "padding: 10px;"
            }
        )
    )

    class Meta:
        model = CustomUser
        fields = ['is_staff', 'is_teacher']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(email__icontains=value) |
                Q(full_name__icontains=value)
            )
        return queryset.all()

class PermissionFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')
    
    content_type = ModelMultipleChoiceFilter(
        queryset=ContentType.objects.all(), 
        label='Тип контента'
    )

    class Meta:
        model = PermissionProxy
        fields = ['content_type']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(codename__icontains=value)
        )

class GroupFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Поиск')
    
    permissions = ModelMultipleChoiceFilter(
        queryset=PermissionProxy.objects.all(),
        label='Права доступа',
        field_name='permissions',
        conjoined=False
    )

    class Meta:
        model = GroupProxy
        fields = ['permissions']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )