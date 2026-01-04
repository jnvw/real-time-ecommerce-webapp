from django.urls import path
from . import views

urlpatterns = [
    # The URL for our new admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
