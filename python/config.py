import os
import logging

logging.basicConfig(level=logging.INFO)

LOG_LEVEL = os.environ['LOG_LEVEL']
FLASK_DEBUG = bool(os.environ['LOG_LEVEL'] == 'debug')

LOCAL = os.environ['LOCAL'].lower() == 'true'

REDIS_URL = os.environ['REDIS_URL']

TWITTER_CONSUMER_TOKEN = os.environ['TWITTER_CONSUMER_TOKEN']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']

TWITTER_SEARCH = os.environ['TWITTER_SEARCH'].split(',')

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

S3_BUCKET = os.environ['S3_BUCKET']
S3_DATA = os.environ['S3_DATA']
