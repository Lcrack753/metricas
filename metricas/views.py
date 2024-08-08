from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.cache import cache_page

from metricas.API_client import YouTubeAPI
from metricas.API_config import YOUTUBE_KEY

import plotly.express as px 

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
        return HttpResponseBadRequest('No user provided')
    data = {
        'channel': youtube.channel_data(),
        'videos': youtube.videos_data()
    }
    return JsonResponse(data, safe=False)



# Create your views here.
def main(request):
    context = {}

    df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
    df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries' # Represent only large countries
    fig = px.pie(df, values='pop', names='country', title='Population of European continent')
    context['fig']=fig.to_html()
    return render(request, 'metricas/main.html',context)