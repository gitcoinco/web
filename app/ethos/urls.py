from django.urls import path, re_path

from . import views

app_name = 'ethos'
urlpatterns = [
    re_path(r'^tweet/?', views.tweet_to_twitter, name='tweet_to_twitter'),
    re_path(r'^render_graph/?', views.render_graph, name='render_graph'),
    re_path(r'^graphzz/?', views.graphzz, name='graphzz'),
    re_path(r'^(.*)/?', views.redeem_coin, name='redeem_coin'),
]
