

from loader import TweetLoader
from enricher import TweetEnricher


if __name__ == '__main__':

    queries = [
        '#bf1',
        '#battlefield1',
        '#battlefieldone',
        '@battlefield'
    ]
    TweetLoader().load(queries)

    files = [
        # '../data/tweets/1465862400.dump',
        # '../data/tweets/1465948800.dump',
        # '../data/tweets/1466035200.dump',
        '../data/tweets/1466121600.dump'
    ]
    TweetEnricher().enrich(files)
