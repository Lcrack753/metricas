from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('api/youtube', views.youtube_api, name='api_youtube')
]
