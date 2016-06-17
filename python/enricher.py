import os
import math
import glob
import json
import datetime

import boto3
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

        if not config.LOCAL:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )

    def records(self, files):

        if not files:
            if config.LOCAL:
                for result in glob.glob('../data/tweets/*/*'):
                    if result.endswith('.dump') and not 'misc' in result:
                        files.append(result)
            else:
                files = []
                paginator = self.s3_client.get_paginator('list_objects')
                for result in paginator.paginate(Bucket=config.S3_BUCKET, Delimiter='%s/tweets' % config.S3_DATA):
                    for content in result['Contents']:
                        if content['Key'].endswith('.dump') and not 'misc' in content['Key']:
                            files.append(content['Key'][len('%s/tweets' % config.S3_DATA):])

        for file_name in files:
            if config.LOCAL:
                for r in self.get(file_name):
                    yield r
            else:
                self.s3_client.download_file('bf1online', 'data/tweets/%s' % file_name, 'local.dump')
                for r in self.get('local.dump'):
                    yield r
                os.remove('local.dump')

    def get(self, file_name):
        with open(file_name, 'r') as f:
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

        # self.db.set('tweet:%s' % result['id_str'], json.dumps(record))

    def _create_groups(self):
        for key in self.db.scan_iter('group:tweet:created_at_hour:*'):
            tweets = self.db.smembers(key)
            self.db.zadd('index:score:created_at_hour', key[len('group:tweet:created_at_hour:'):], len(tweets))

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
