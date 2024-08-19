from dotenv import load_dotenv
import os

load_dotenv()

# Keys
YOUTUBE_KEY = os.getenv('YOUTUBE_KEY')
INSTAGRAM_KEY = os.getenv('INSTAGRAM_KEY')

BEARER_TOKEN = os.getenv('BEARER_TOKEN')
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

FACEBOOK_KEY = os.getenv('FACEBOOK_KEY')

DEFAULT_IMG_URL = 'https://upload.wikimedia.org/wikipedia/commons/6/65/Baby.tux-800x800.png'

# Youtube
YOUTUBE_MAX_RESULTS = 20
TWITTER_MAX_RESULTS = 20

