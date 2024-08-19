from django.test import TestCase

# Create your tests here.
from ntscraper import Nitter
from pprint import pprint

scraper = Nitter(log_level=1, skip_instance_check=False)

# github_hash_tweets = scraper.get_tweets("github", mode='hashtag')

bezos_tweets = scraper.get_tweets("JeffBezos", mode='user',number=10)

bezos_information = scraper.get_profile_info("JeffBezos")

pprint(bezos_tweets)