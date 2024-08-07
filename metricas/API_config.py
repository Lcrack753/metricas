from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

YOUTUBE_KEY = os.getenv('YOUTUBE_KEY')
INSTAGRAM_KEY = os.getenv('INSTAGRAM_KEY')
X_KEY = os.getenv('X_KEY')
FACEBOOK_KEY = os.getenv('FACEBOOK_KEY')
