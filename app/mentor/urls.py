from django.urls import path

from . import views

urlpatterns = [
    path('', views.mentors, name='mentor_list'),
    path('fetch', views.mentors_fetch, name='mentors_fetch'),
    path('profile', views.mentor, name='mentor'),
    path('<int:mentor_id>/profile', views.show_mentor, name='mentor_details')
]
