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

        return clean_data
    
    def chart_views(self, videos: list[dict] = None):
        if not videos:
            data = self.clean_data()
            videos = data.get('videos', [])
        
        assert len(videos) > 1, 'there must be more than one video'

        date_views = [(video.get('publishedAt'), video.get('statistics').get('viewCount')) for video in videos]
        df = pd.DataFrame.from_records(date_views, columns=['Date', 'Views'])
        fig = px.line(df, x='Date', y='Views')
        
        # Set layout options for responsive behavior
        fig.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title='Date',
            yaxis_title='Views',
            height = 400,
            # width = 'auto'

        )
        
        fig.update_xaxes(
            ticks="outside",
            ticklabelmode="period",
            tickcolor="black",
            ticklen=10,
            minor=dict(
                ticklen=4,
                dtick=7*24*60*60*1000,
                tick0="2016-07-03",
                griddash='dot',
                gridcolor='white'
            )
        )
        
        return fig
            
if __name__ == '__main__':
    graph = YoutubeStatistics(URL)
    fig = graph.chart_views()
    fig.show()
