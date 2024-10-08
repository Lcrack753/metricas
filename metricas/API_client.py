import dateparser.parser
from metricas.API_config import *
from .utils import *
import requests
import os
import json
import hashlib
from pprint import pprint
from datetime import datetime
import dateparser
from ntscraper import Nitter #Scrapper For twitter
import plotly.graph_objects as go

from .models import Response
from django.http import HttpRequest

# Cache Manage
BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(BASE_DIR, 'cache_directory')

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def generate_cache_key(endpoint: str, params: dict) -> str:
    """Generates a unique cache key from the endpoint and parameters"""
    key = f'{endpoint}_{json.dumps(params, sort_keys=True)}'
    return hashlib.md5(key.encode('utf-8')).hexdigest()

def get_cache_file_path(cache_key: str) -> str:
    """Generate cache file path based on key"""
    return os.path.join(CACHE_DIR, f'{cache_key}.json')

def save_to_cache(cache_key: str, data: dict, etag: str = None) -> None:
    """Saves data in a cache file along with the ETag"""
    file_path = get_cache_file_path(cache_key)
    cache_data = {
        'data': data,
        'etag': etag
    }
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(cache_data, file)

def read_from_cache(cache_key: str) -> dict:
    """Reads data from a cache file"""
    file_path = get_cache_file_path(cache_key)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def clear_cache():
    """Clear all cache files"""
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

class APIClient:
    def __init__(self, base_url: str, api_key: str = None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def _make_request(self, endpoint: str, params: dict = None, headers: dict = None) -> dict:
        if params is None:
            params = {}
        if self.api_key:
            params['key'] = self.api_key

        cache_key = generate_cache_key(endpoint, params)
        cached_response = read_from_cache(cache_key)
        
        if headers is None:
            headers = {}
        if cached_response and 'etag' in cached_response:
            headers['If-None-Match'] = cached_response['etag']

        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
            if response.status_code == 304:
                # Return cached response if server indicates not modified
                print(f"Using cached response (304 Not Modified)\nrequest: {self.base_url+endpoint}\nparams: {params}\n")
                return cached_response['data']

            response.raise_for_status()
            data = response.json()
            etag = self.extract_etag(response)
            if 'error' in data:
                print(f"API Error: {data['error']['message']}")
                return {}

            # Save the new data to cache
            save_to_cache(cache_key, data, etag)
            print(f"New Cache\nrequest: {self.base_url+endpoint}\nparams: {params}\n")

            return data
        except requests.HTTPError as e:
            print(f"HTTP error occurred: {e}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        return {}

    def extract_etag(self, response: requests.Response) -> str:
        """Extracts ETag from the response headers"""
        # Default implementation; can be overridden in subclasses
        return response.headers.get('ETag','')


class YouTubeAPI(APIClient):
    def __init__(self, api_key: str, userId: str = None, userName: str = None) -> None:
        super().__init__('https://www.googleapis.com/youtube/v3', api_key)
        self._userId = userId
        self._userName = userName

    
    @property
    def userId(self):
        return self._userId
    
    @userId.setter
    def userId(self, value):
        self._userId = value

    @property
    def userName(self):
        return self._userName
    
    @userName.setter
    def userName(self, value):
        assert '@' in value and not ' ' in value, 'Error: userName must have @ and not spaces'
        
        params = {
            'forHandle': value,
            'part': 'id'
        }
        response = self._make_request('/channels', params=params)
        
        assert response['pageInfo']['totalResults'] == 1, 'Error: more than one channel'

        self._userId = response['items'][0]['id']
        self._userName = value

    @userName.getter
    def userName(self):
        if self._userName:
            return self._userName
        
        params = {
            'id': self._userId,
            'part': 'snippet'
        }
        response = self._make_request('/channels', params=params)
        
        assert response['pageInfo']['totalResults'] == 1, 'Error: more than one channel'

        self._userName = response['items'][0]['snippet']['customUrl']
        return self._userName

    def extract_etag(self, response: requests.Response) -> str:
        """Extracts ETag from the response body for YouTube API"""
        return response.json().get('etag')

    def channel_data(self) -> dict:
        """Get data from a channel"""
        if not self._userId:
            print('Error: Must define userId')
            return {}
        
        params = {
            'part': 'statistics,status,snippet',
            'id': self._userId
        }

        response = self._make_request('/channels', params=params)
        result = response['pageInfo']['totalResults']
        
        if result != 1:
            print(f'Error: there are {result} results')
            return {}
        return response

    def _channel_videos(self) -> dict:
        """Get channel videos search response"""
        if not self._userId:
            print('Error: Must define userId')
            return {}
        
        params = {
            'channelId': self._userId,
            'maxResults': YOUTUBE_MAX_RESULTS if YOUTUBE_MAX_RESULTS else 10,
            'order': 'date',
            'type': 'video',
        }

        response = self._make_request('/search', params)
        return response
    
    def channel_videos_id(self) -> list[str]:
        """Cleared channel videos search response"""
        data = self._channel_videos()
        if not data:
            print('Error: Data channel videos does not have content')
            return {}
        return [video['id']['videoId'] for video in data['items']]

    def videos_data(self, videos_ids: list[str] = None):
        if not videos_ids:
            videos_ids = self.channel_videos_id()
        if len(videos_ids) < 1:
            print('Error: Videos ids blank')
            return {}
        videos_ids_txt = ''
        for videoId in videos_ids:
            videos_ids_txt += videoId + ','
        params = {
            'part': 'id,snippet,statistics',
            'id': videos_ids_txt
        }
        return self._make_request('/videos',params)


class TwitterScraper:
    """Scrape Twitter profile and tweets data"""

    def __init__(self, log_level: int = 1, skip_instance_check: bool = False):
        self.log_level = log_level
        self.skip_instance_check = skip_instance_check
        

    def _get_tweets(self, username: str, number: int = 20) -> dict:
        try:
            return self.scraper.get_tweets(username, mode='user', number=number).get('tweets', [])
        except Exception as e:
            print(f"Error obteniendo tweets: {e}")
            return []

    def _get_profile_info(self, username: str) -> dict:
        try:
            return self.scraper.get_profile_info(username)
        except Exception as e:
            print(f"Error obteniendo perfil: {e}")
            return {}
        
    def get_data(self, username: str, number: int = 20) -> tuple:
        """
        Get profile data and tweets based on the username
        :param username: username of the twitter profile
        :param number: max number of tweets scraped
        :return: tuple like (profile_info, profile_tweets) 
        """
        self.scraper = Nitter(log_level=self.log_level, skip_instance_check=self.skip_instance_check)
        return (self._get_profile_info(username),self._get_tweets(username,number))

class TwitterData:
    
    """Handle TwitterScraper return data"""
    def clean_data(self, data: tuple = None) -> dict:
        """
        Clear data from TwitterScraper 
        """
        if data:
            userinfo, tweets = data
        else:
            print('Error: No Data, excecute get_data()')
            return {}
        username = userinfo.get('username', '')[1:]
        tweets = [tweet for tweet in tweets if tweet.get('link').find(username) != -1]
        data = {
            'profile': {},
            'tweets': []
        }
        more_statistics = {'avgRetweets':0, 'avgLikes':0,'avgComments':0, 'avgQuotes':0}

        for tweet in tweets:
            stats = tweet.get('stats', {})
            d = {
                'user': tweet.get('user', {}),
                'url': tweet.get('link','#'),
                'text': tweet.get('text', ''),
                'picture': tweet.get('pictures', [DEFAULT_IMG_URL])[0] if tweet.get('pictures') else '',
                'video': tweet.get('videos', ['No video Found']),
                'statistics': stats,
                'datetime': dateparser.parse(tweet.get('date', '26/06/2003 15:00')).isoformat()
            }
            data['tweets'].append(d)

            more_statistics['avgRetweets'] += int(stats.get('retweets', 0))   
            more_statistics['avgLikes'] += int(stats.get('likes', 0))   
            more_statistics['avgComments'] += int(stats.get('comments', 0))   
            more_statistics['avgQuotes'] += int(stats.get('quotes', 0))   

        total_tweets = len(tweets)
        if total_tweets > 0:
            more_statistics = {key: str(round(value / total_tweets)) for key, value in more_statistics.items()}
        else:
            more_statistics = {key: 0 for key, value in more_statistics.items()}
        data['profile'] = userinfo
        data['profile']['joined'] = dateparser.parse(userinfo.get('joined','26/06/2003 15:00')).isoformat()
        data['profile']['stats'].update(more_statistics) 
        
        return data
        
class TwitterAPI:
    def __init__(self, username: str) -> None:
        self.username = username
        self.scrape = TwitterScraper()
        self.cleaner = TwitterData()
        self.data = None
    
    def str_data(self):
        pprint(self.data)

    def make_requests(self):
        try:
            response = self.scrape.get_data(self.username)
            userinfo, tweets = response
            if not userinfo or not tweets:
                raise ValueError('Make Request Fallida')
            self.data = self.cleaner.clean_data(response)
            save_response(
                service='Twitter',
                params={'userName': self.username},
                response=self.data
            )
            return self.data        
        except Exception as e:
            print(e)
        return {}
    
    def search_responses(self):
        responses = search_responses(
                        service='Twitter',
                        params={'userName': self.username}
                    )
        if not responses.exists():
            print('Error: Responses not found')
            return None
        return responses    
    
    def last_response(self):
        response = self.search_responses()
        if not response:
            print('Error: Response not found')
            return None
        self.data = response.first().response
        return self.data