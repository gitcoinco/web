from django.urls import re_path

from . import views

app_name = 'ethos'
urlpatterns = [
    re_path(r'^img/?', views.image_gen, name='ethos_img'),
    re_path(r'^tweet/?', views.tweet_to_twitter, name='tweet_to_twitter'),
    re_path(r'^(.*)/?', views.redeem_coin, name='redeem_coin'),
]
