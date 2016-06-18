import os
import time
import json
import shutil
import logging
import datetime
import tempfile

import boto3
import tweepy

import config
from utils import dt2ts, round_to_nearest_day

log = logging.getLogger(__name__)


class Loader:
    def load(self):
        pass


class TweetLoader(Loader):

    def __init__(self):
        self.auth = tweepy.OAuthHandler(
            config.TWITTER_CONSUMER_TOKEN,
            config.TWITTER_CONSUMER_SECRET
        )
        self.twitter = tweepy.API(self.auth)

        if not config.LOCAL:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )

    def get_tweets(self, query, since_id):
        c = tweepy.Cursor(
            self.twitter.search,
            q=query,
            rpp=100,
            count=100,
            since_id=str(since_id)
        ).items()

        while True:
            try:
                tweet = c.next()
                log.info('%s - %s', tweet.id, tweet.created_at)
                yield tweet
            except tweepy.TweepError:
                time.sleep(60 * 15)
                continue
            except StopIteration:
                break

    def load(self, queries):
        name = dt2ts(round_to_nearest_day(datetime.datetime.utcnow()))

        output = []
        for query in queries:

            if config.LOCAL:
                marker_file = 'tmp/%s.marker' % query
            else:
                marker_file = '%s.marker' % query
                self.s3_client.download_file('bf1online', 'data/tweets/%s.marker' % query, marker_file)

            if os.path.isfile(marker_file):
                with open(marker_file, 'r') as f2:
                    since_id = f2.read() or None
            else:
                since_id = None

            file_name = ''
            with tempfile.NamedTemporaryFile(delete=False, mode='a') as f:
                file_name = f.name
                next_id = None
                for tweet in self.get_tweets(query, since_id):
                    record = tweet._json
                    record['imported_at'] = str(datetime.datetime.utcnow())
                    f.write(json.dumps(record))
                    f.write('\n')
                    if not next_id:
                        next_id = tweet.id

            if next_id:
                if os.path.dirname(marker_file):
                    os.makedirs(os.path.dirname(marker_file), exist_ok=True)
                with open(marker_file, 'w') as f2:
                    f2.write(str(next_id))

            if config.LOCAL:
                location = 'tmp/%s/%s.dump' % (query, datetime.datetime.now())
                os.makedirs(os.path.dirname(location), exist_ok=True)
                shutil.move(file_name, location)
                output.append(location)
            else:
                location = '%s/%s.dump' % (query, datetime.datetime.now())
                self.s3_client.upload_file('%s.marker' % query, 'bf1online', '%s/tweets/%s.marker' % (config.S3_DATA, query))
                self.s3_client.upload_file(file_name, 'bf1online', '%s/tweets/%s' % (config.S3_DATA, location))
                os.remove('%s.marker' % query)
                os.remove(file_name)
                output.append(location)

        return output
