from django.urls import path

from . import views

urlpatterns = [
    path('', views.mentors, name='mentor_list'),
    path('fetch', views.MentorsList.as_view(), name='mentor_fetch'),
    path('<int:pk>', views.MentorDetail.as_view(), name='mentor_details')
]
