from django.urls import path
from Curriculum.AccessControl.views import *

urlpatterns = [
    path('users/', UserTableView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/change_password/', UserPasswordChangeView.as_view(), name='user_change_password'),

    path('groups/', GroupTableView.as_view(), name='group_list'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/update/', GroupUpdateView.as_view(), name='group_update'),
    path('groups/create/', GroupCreateView.as_view(), name='group_create'),

    path('permissions/', PermissionTableView.as_view(), name='permission_list'),
    path('permissions/<int:pk>/', PermissionDetailView.as_view(), name='permission_detail'),
    path('permissions/<int:pk>/update/', PermissionUpdateView.as_view(), name='permission_update'),
    path('permissions/create/', PermissionCreateView.as_view(), name='permission_create'),
]