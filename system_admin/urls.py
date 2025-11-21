from django.urls import path
from . import views

app_name = 'system_admin'

urlpatterns = [
    path('', views.system_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/create/', views.user_create, name='user_create'),
    path('settings/', views.system_settings, name='settings'),
    path('statistics/', views.system_statistics, name='statistics'),
]

