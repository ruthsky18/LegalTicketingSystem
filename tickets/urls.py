from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/conversation/', views.user_ticket_conversation, name='user_ticket_conversation'),
    # Legal team admin routes
    path('legal/', views.admin_dashboard, name='admin_dashboard'),
    path('legal/ticket/<int:ticket_id>/', views.admin_ticket_detail, name='admin_ticket_detail'),
    path('legal/ticket/<int:ticket_id>/conversation/', views.ticket_conversation, name='ticket_conversation'),
    path('legal/ticket/<int:ticket_id>/download/', views.download_document, name='download_document'),
    path('legal/ticket/<int:ticket_id>/download-reviewed/', views.download_reviewed_document, name='download_reviewed_document'),
]
