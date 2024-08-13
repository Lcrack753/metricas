from dotenv import load_dotenv
import os

load_dotenv()

# Keys
YOUTUBE_KEY = os.getenv('YOUTUBE_KEY')
INSTAGRAM_KEY = os.getenv('INSTAGRAM_KEY')
X_KEY = os.getenv('X_KEY')
FACEBOOK_KEY = os.getenv('FACEBOOK_KEY')

# Youtube
MAX_RESULTS = 20