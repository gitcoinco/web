from django.conf.urls import url

from experts.consumers import ExpertSessionConsumer

websocket_urlpatterns = [
    url(r'^ws/experts/sessions/(?P<session_id>[^/]+)/$', ExpertSessionConsumer),
]
