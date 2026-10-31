from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('address/new/', views.address_create_view, name='address_create'),
    path('address/<int:pk>/edit/', views.address_edit_view, name='address_edit'),
    path('address/<int:pk>/delete/', views.address_delete_view, name='address_delete'),
    path('support/', views.support_tickets_view, name='support_tickets'),
    path('support/<int:pk>/', views.ticket_detail_view, name='ticket_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read_view, name='mark_notification_read'),
]
