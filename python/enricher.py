import math
import json
import datetime

import redis
from dateutil.parser import parse

import config
from utils import dt2ts, round_to_nearest_hour


class Enricher:

    def records(self):
        pass

    def enrich(self):
        pass


class TweetEnricher(Enricher):

    def __init__(self):
        self.db = redis.Redis()

    def records(self, files):

        for fname in files:
            with open(fname, 'r') as f:
                for l in f.readlines():
                    result = json.loads(l)
                    if result['lang'] == 'en' and (not 'giveaway' in result['text'].lower()):
                        yield result

    def enrich(self, files):
        for result in self.records(files):
            self._create_reverse_indexes(result)

        self._create_groups()
        self._create_scores()

    def _create_reverse_indexes(self, result):
        created_at = parse(result['created_at'])

        self.db.sadd('group:tweet:created_at_hour:%s' % dt2ts(round_to_nearest_hour(created_at)), result['id_str'])

        for group, attribute, function in [
            ('media', 'media_url_https', lambda x: x),
            ('user_mentions', 'screen_name', lambda x: x.lower()),
            ('hashtags', 'text', lambda x: x.lower())
        ]:
            if result['entities'].get(group):
                for r in result['entities'][group]:
                    self.db.zadd('index:tweet:%s:%s' % (group, function(r[attribute])), result['id_str'], dt2ts(created_at))

        record = {
            'id_str': result['id_str'],
            'created_at': result['created_at'],
            'text': result['text'],
            'original_id_str': result['retweeted_status']['id_str'] if 'retweeted_status' in result else None
        }

        self.db.set('tweet:%s' % result['id_str'], json.dumps(record))

    def _create_groups(self):
        for key in self.db.scan_iter('group:tweet:created_at_hour:*'):
            tweets = self.db.smembers(key)
            self.db.zadd('index:score:created_at_hour_popularity', key[len('group:tweet:created_at_hour:'):], len(tweets))

            self.db.zadd('index:score:created_at_hour_counts', key[len('group:tweet:created_at_hour:'):], len(tweets))

    def _create_scores(self):
        for group in [
            'media',
            'user_mentions',
            'hashtags'
        ]:

            now = dt2ts(datetime.datetime.utcnow())
            for key in self.db.scan_iter('index:tweet:%s:*' % group):
                score = 0
                for tweet, posted in self.db.zrangebyscore(key, now - (60 * 60 * 24 * 5), now, withscores=True):
                    time_ago = now - posted
                    hours_ago = time_ago//3600 or 1

                    s = math.log(1/(hours_ago**20)) + 100
                    if s > 0:
                        score += s

                self.db.zadd('index:score:%s' % group, key[len('group:tweet:%s:' % group):], score)
