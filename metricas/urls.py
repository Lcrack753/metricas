from django.urls import path
from . import views
from django.shortcuts import redirect


urlpatterns = [
    path('', views.main, name='main'),
    path('youtube', views.youtube, name='youtube'),
    path('api/youtube', views.youtube_api, name='api_youtube')
]
