from .views import *
from django.urls import path
from Academhub.utils import getpattern

urlpatterns = [
    path('user/list', UserTableView.as_view(), name = getpattern('CustomUser', 'list')),
    path('user/create', UserCreateView.as_view(), name = getpattern('CustomUser', 'add')),
    path('user/<int:pk>', UserDetailView.as_view(), name = getpattern('CustomUser', 'detail')),
    path('user/change/<int:pk>', UserUpdateView.as_view(), name = getpattern('CustomUser', 'change')),

    path('permission/list', PermissionTableView.as_view(), name = getpattern('PermissionProxy', 'list')),
    path('permission/create', PermissionCreateView.as_view(), name = getpattern('PermissionProxy', 'add')),
    path('permission/<int:pk>', PermissionDetailView.as_view(), name = getpattern('PermissionProxy', 'detail')),
    path('permission/change/<int:pk>', PermissionUpdateView.as_view(), name = getpattern('PermissionProxy', 'change')),

    path('group/list', GroupTableView.as_view(), name = getpattern('GroupProxy', 'list')),
    path('group/create', GroupCreateView.as_view(), name = getpattern('GroupProxy', 'add')),
    path('group/<int:pk>', GroupDetailView.as_view(), name = getpattern('GroupProxy', 'detail')),
    path('group/change/<int:pk>', GroupUpdateView.as_view(), name = getpattern('GroupProxy', 'change')),
]