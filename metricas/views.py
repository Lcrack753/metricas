from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.cache import cache_page
from django.urls import reverse


from metricas.API_client import YouTubeAPI, TwitterAPI
from metricas.API_config import *
from metricas.graphs import YoutubeStatistics
import plotly.express as px 
import copy

def main(request):
    pass


@cache_page(60 * 100)
def twitter_api(request):
    userName = request.GET.get('userName')
    if not userName:
        return HttpResponseBadRequest('No userName provided')
    twitter = TwitterAPI(userName)
    
    return JsonResponse(twitter.clean_data(), safe=False)

@cache_page(60 * 10)
def youtube_api(request):
    userName = request.GET.get('userName')
    userId = request.GET.get('userId')
    youtube = YouTubeAPI(YOUTUBE_KEY)
    if userName:
        youtube.userName = userName
    elif userId:
        youtube.userId = userId
    else:
        return HttpResponseBadRequest('No userName or userID provided')
    data = {
        'channel': youtube.channel_data(),
        'videos': youtube.videos_data()
    }
    return JsonResponse(data, safe=False)



# Create your views here.
def youtube(request):
    context = {}
    
    userName = '@joerogan'
    full_url = request.build_absolute_uri(reverse('api_youtube')) + f'?userName={userName}' 
    # userId = 'UCbJHfnWtshjo6zJg9Y8XzBw'
    # full_url = request.build_absolute_uri(reverse('api_youtube')) + f'?userId={userId}' 
    print(full_url)
    youtube_statistics = YoutubeStatistics(full_url)
    
    fig = youtube_statistics.chart_views()
    context['fig'] = fig.to_html()
    
    data = youtube_statistics.clean_data()
    videos = data['videos'] # [:5]  + data['videos'][:5] + data['videos'][:5] +data['videos'][:5]
    context['data'] = data
    context['videos'] = videos
    return render(request, 'metricas/youtube.html',context)

def twitter(request):
    return render(request,'metricas/twitter.html')