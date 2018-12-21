from django.urls import path
from inbox import views


app_name = 'inbox'
urlpatterns = [
    path('', views.inbox, name='inbox_view'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/delete/', views.delete_notifications, name='delete_notifications'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('notifications/read/', views.read_notifications, name='read_notifications'),
]