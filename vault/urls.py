from django.urls import path

from . import views

app_name = 'vault'

urlpatterns = [
    path('', views.LicenseListView.as_view(), name='license_list'),
    path('licenses/new/', views.LicenseCreateView.as_view(), name='license_create'),
    path('licenses/<int:pk>/', views.LicenseDetailView.as_view(), name='license_detail'),
    path('licenses/<int:pk>/edit/', views.LicenseUpdateView.as_view(), name='license_update'),
    path('licenses/<int:pk>/delete/', views.LicenseDeleteView.as_view(), name='license_delete'),
    path('licenses/<int:pk>/access/', views.LicenseAccessView.as_view(), name='license_access'),
]
