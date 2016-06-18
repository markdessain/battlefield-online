import sys

import config
from loader import TweetLoader
from enricher import TweetEnricher


if __name__ == '__main__':

    args = sys.argv

    if len(args) > 1:
        plan = args[1]
    else:
        plan = 'load-enrich'

    if 'load' in plan:
        queries = config.TWITTER_SEARCH
        files = TweetLoader().load(queries)
    else:
        files = []

    if 'enrich' in plan:
        TweetEnricher().enrich(files)
