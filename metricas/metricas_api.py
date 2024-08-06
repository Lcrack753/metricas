from .config import YOUTUBE_KEY, INSTAGRAM_KEY, X_KEY, FACEBOOK_KEY

import requests
from pprint import pprint
class MetricasKeys():
    """Object for handind keys"""

    def __init__(self,
                 youtube_key: str = None,
                 instagram_key: str = None,
                 x_key: str = None,
                 facebook_key: str = None
                 ) -> None:
        self._youtube_key = youtube_key
        self._instagram_key = instagram_key
        self._x_key = x_key
        self._facebook_key = facebook_key

    @property
    def youtube(self):
        return self._youtube_key
    
    @youtube.setter
    def youtube(self, value):
        self._youtube_key = value

    @property
    def instagram(self):
        return self._instagram_key
    
    @instagram.setter
    def instagram(self, value):
        self._instagram_key = value

    @property
    def x(self):
        return self._x_key
    
    @x.setter
    def x(self, value):
        self._x_key = value

    @property
    def facebook(self):
        return self._facebook_key
    
    @facebook.setter
    def facebook(self, value):
        self._facebook_key = value

    def _validate_youtube_key(self, key: str = None) -> bool:
        if key is None:
            key = self._youtube_key

        if not key:
            print("Error: No API key provided.")
            return False

        try:
            response = requests.get(f'https://www.googleapis.com/youtube/v3/search',
                                    params={
                                        'key': key
                                    })
            
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print(f"Error: {data['error']['message']}")
                    return False
                return True

            else:
                print(f"Error: HTTP {response.status_code} - {response.reason}")
                return False

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return False

    def _validate_instagram_key(self, key: str) -> bool:
        return True if key else False

    def _validate_x_key(self, key: str) -> bool:
        return True if key else False

    def _validate_facebook_key(self, key: str) -> bool:
        return True if key else False
    


if __name__ == '__main__':
    keys = MetricasKeys()
    keys.youtube = YOUTUBE_KEY
    print(keys._validate_youtube_key())
