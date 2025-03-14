from django.urls import path, include
from django.contrib.auth.views import LogoutView
from Curriculum import views
from django.contrib import admin

urlpatterns = [
    # path("prometheus/", include("django_prometheus.urls")),

    path('admin/', admin.site.urls),

    path('', views.HomeView.as_view(), name='home'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('auth/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('ContingentApp/', include('Curriculum.Сontingent.urls')),
    path('AccessControl/', include('Curriculum.AccessControl.urls')),
    path('GradeBookApp/', include('Curriculum.Gradebook.urls')),
]