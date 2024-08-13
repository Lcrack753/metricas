from typing import Dict, List, Optional
import requests
from pprint import pprint
from datetime import datetime
import plotly.express as px
import pandas as pd

URL = 'http://127.0.0.1:8000/api/youtube?userId=UC_R6ZS7eKS8wZgJaOnc-9rA'
DEFAULT_IMG_URL = 'https://upload.wikimedia.org/wikipedia/commons/6/65/Baby.tux-800x800.png'

class StatisticsRequest:
    def __init__(self, url: str) -> None:
        self.url = url
        self.data: Optional[Dict] = None
        self._fetch_data()
    
    def _fetch_data(self) -> None:
        """Fetch data from the provided URL and handle errors."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.data = response.json()
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        except ValueError as e:
            print(f"Error parsing JSON: {e}")

class YoutubeStatistics(StatisticsRequest):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def clean_data(self) -> Dict[str, Optional[Dict[str, str]]]:
        """Extract and clean specific data from the fetched JSON."""
        clean_data = {
            'channel': {},
            'videos': []
        }
        if not self.data:
            raise ValueError('Error: There is no data')
        
        # Channel Info
        channel_items = self.data.get('channel', {}).get('items', [])
        if not channel_items:
            clean_data['channel']['title'] = 'No items available'
            clean_data['channel']['thumbnail'] = DEFAULT_IMG_URL
            clean_data['channel']['statistics'] = {}

        snippet = channel_items[0].get('snippet', {})
        clean_data['channel']['title'] = snippet.get('title', 'No title available')
        clean_data['channel']['thumbnail'] = snippet.get('thumbnails', {}).get('high', {}).get('url', DEFAULT_IMG_URL) # 800 x 800
        clean_data['channel']['statistics'] = channel_items[0].get('statistics', {})

        # Videos Info
        videos = self.data.get('videos', {}).get('items', [])
        for video in videos:
            snippet = video.get('snippet', {})
            clean_data['videos'].append({
                'url': video.get('id', 'No id available'),
                'title': snippet.get('title', 'No title available'),
                'publishedAt': snippet.get('publishedAt', 'No date available'),
                'thumbnail': snippet.get('thumbnails', {}).get('standard', {}).get('url', DEFAULT_IMG_URL), # 640 x 480
                'statistics': video.get('statistics', {}),
                'datetime': datetime.strptime(snippet.get('publishedAt', '2024-01-01'),r"%Y-%m-%dT%H:%M:%SZ"),
            })

        # Additionals Statisctics, deppends of videos max results
        total_videos = len(videos)
        more_statistics = {'avgViews':0, 'avgLikes':0,'avgComments':0}
        for video in clean_data.get('videos', []):
            statistics =  video.get('statistics', {})
            more_statistics['avgViews'] += int(statistics.get('viewCount', 0))
            more_statistics['avgLikes'] += int(statistics.get('likeCount', 0))
            more_statistics['avgComments'] += int(statistics.get('commentCount', 0))
        more_statistics = {key: str(round(value / total_videos)) for key, value in more_statistics.items()}
        
        clean_data['channel']['statistics'].update(more_statistics)

        return clean_data
    
    def chart_views(self, videos: list[dict] = None):
        if not videos:
            data = self.clean_data()
            videos = data.get('videos', [])
        
        # Procesar los datos
        date_views = [(video.get('datetime'), video.get('statistics').get('viewCount'), video.get('title')) for video in videos]
        df = pd.DataFrame.from_records(date_views, columns=['Date', 'Views', 'Title'])
        df['Date'] = pd.to_datetime(df['Date'])
        df['Views'] = pd.to_numeric(df['Views'], errors='coerce')

        # Crear el gráfico de barras
        fig = px.bar(df, x='Title', y='Views', hover_data={'Title': True, 'Views': True})

        # Agregar el título completo a customdata
        fig.update_traces(
            marker_color='#a10000',
            customdata=df[['Title']],  # Agrega el título completo a customdata
            hovertemplate='<b>%{customdata[0]}</b><br>Views: %{y}<extra></extra>'  # Usa customdata para mostrar el título completo
        )

        # Personalización del diseño
        fig.update_layout(
            autosize=True,
            margin=dict(l=10, r=10, t=40, b=80),  # Ajusta márgenes para mejor presentación
            xaxis_title='Video',
            yaxis_title='Views',
            height=400,
            xaxis_tickangle=-45,  # Rota las etiquetas del eje x para mejor visibilidad
            yaxis_type='log',  # Eje Y logarítmico
            xaxis=dict(
                tickmode='array',
                tickvals=df['Title'],
                ticktext=['...' + title[-15:] if len(title) > 15 else title for title in df['Title']]  # Recorta los títulos largos
            ),
            plot_bgcolor='white',  # Fondo blanco para el gráfico
            font=dict(size=12, color='black', family='roboto'),  # Fuente más legible
            title_font=dict(size=16, family='roboto', color='black')  # Fuente para el título
        )

        return fig

        
    def engagement(self):
        videos = self.clean_data().get('videos', [])
        if len(videos) < 1:
            print('Error: No data.items or more than 1')
            return {}
        
        avgs = []
        views = 0
        for video in videos:
            statistics = video.get('statistics', {})
            views += int(statistics.get('viewCount', 0))
            actions = (int(statistics.get('likeCount', 0)) + 
                        int(statistics.get('commentCount', 0)) +
                        int(statistics.get('favoriteCount', 0)))
            avgs.append((actions/views) * 100)
        return f"{views / len(videos):.0f}"

if __name__ == '__main__':
    graph = YoutubeStatistics(URL)
    fig = graph.chart_views()
    fig.show()
