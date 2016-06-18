import json
import logging
import datetime

import redis
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

import config


log = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../html', static_folder='../static')
app.config['DEBUG'] = config.FLASK_DEBUG

db = redis.from_url(config.REDIS_URL)


@app.route('/')
def route_index():
    return render_template('index.html', google_tracking_id=config.GOOGLE_TRACKING_ID)


@app.route('/graph')
def route_graph():
    def get_groups(group):
        return dict([
            (int(timestamp), int(score))
            for timestamp, score in db.zrangebyscore('index:score:%s' % group, '-inf', '+inf', withscores=True)
        ])

    created_at_hour = get_groups('created_at_hour')
    retweets_at_hour = get_groups('retweets_at_hour')

    all_timestamps = sorted(set(created_at_hour.keys()).union(set(retweets_at_hour.keys())))

    created_at_hour_result = []
    retweets_at_hour_result = []
    labels = []

    for timestamp in all_timestamps:

        created_at_hour_result.append(
            created_at_hour.get(timestamp, 0)
        )
        retweets_at_hour_result.append(
            retweets_at_hour.get(timestamp, 0)
        )

        labels.append(
            datetime.datetime.utcfromtimestamp(timestamp)
        )

    labels = map(
        lambda x: '%s %s:00' % (x.strftime('%a'), x.hour) if x.hour == 0 else '%s:00' % x.hour if x.hour % 4 ==0 else '',
        labels
    )

    result = {
        'labels': list(labels),
        'datasets': {
            'created_at_hour': created_at_hour_result,
            'retweets_at_hour': retweets_at_hour_result
        }

    }

    return jsonify(result)


@app.route('/top')
def route_top():
    result = {
        'media': [
            url.decode()
            for url in db.zrange('index:score:media', 0, 20, desc=True)
        ],
        'hashtags': [
            url.decode()
            for url in db.zrange('index:score:hashtags', 0, 20, desc=True)
        ],
        'user_mentions': [
            url.decode()
            for url in db.zrange('index:score:user_mentions', 0, 18, desc=True)
        ]
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run()
