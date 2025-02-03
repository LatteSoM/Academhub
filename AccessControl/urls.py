from .views import *
from django.urls import path

urlpatterns = [
    path('user/list', UserTableView.as_view(), name='customuser_list'),
    path('user/create', UserCreateView.as_view(), name='customuser_create'),
    path('user/<int:pk>', UserDetailView.as_view(), name='customuser_ditail'),
    path('user/update/<int:pk>', UserUpdateView.as_view(), name='customuser_update'),

    path('permission/list', PermissionTableView.as_view(), name='permissionproxy_list'),
    path('permission/create', PermissionCreateView.as_view(), name='permissionproxy_create'),
    path('permission/<int:pk>', PermissionDetailView.as_view(), name='permissionproxy_ditail'),
    path('permission/update/<int:pk>', PermissionUpdateView.as_view(), name='permissionproxy_update'),

    path('group/list', GroupTableView.as_view(), name='groupproxy_list'),
    path('group/create', GroupCreateView.as_view(), name='groupproxy_create'),
    path('group/<int:pk>', GroupDetailView.as_view(), name='groupproxy_ditail'),
    path('group/update/<int:pk>', GroupUpdateView.as_view(), name='groupproxy_update'),
]