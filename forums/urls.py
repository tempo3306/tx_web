from django.urls import path
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('boards/<str:slug>/', views.board_topics, name='board_topics'),
    path('boards/<str:slug>/new/', views.new_topic, name='new_topic'),
    path('boards/<str:slug>/<str:topic_slug>/', views.topic_posts, name='topic_posts'),
    path('boards/<str:slug>/<str:topic_slug>/reply/', views.reply_topic, name='reply_topic'),
    url('^test/$', views.test, name='test'),
    url('^change_profile/$', views.change_profile, name='change_profile')
]
