import time
import json
import logging
import datetime

import tweepy

import config
from utils import dt2ts, round_to_nearest_day

log = logging.getLogger(__name__)


class Loader:
    def load(self):
        pass


class TweetLoader(Loader):

    def __init__(self):
        self.auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_TOKEN, config.TWITTER_CONSUMER_SECRET)
        self.twitter = tweepy.API(self.auth)

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
        with open('../data/tweets/%s.dump' % name, 'a') as f:
            for query in queries:

                with open('../data/tweets/%s.marker' % query, 'r') as f2:
                    since_id = f2.read() or None
                next_id = None
                for tweet in self.get_tweets(query, since_id):
                    record = tweet._json
                    record['imported_at'] = str(datetime.datetime.utcnow())
                    f.write(json.dumps(record))
                    f.write('\n')
                    if not next_id:
                        next_id = tweet.id

                if next_id:
                    with open('../data/tweets/%s.marker' % query, 'w') as f2:
                        f2.write(str(next_id))
